""" A module for creating Solana nodes on AWS. """

from typing import Union, Optional

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
import pulumi_svmkit as svmkit

from .network import external_sg, internal_sg

AGAVE_VERSION = "1.18.24-1"

ami = aws.ec2.get_ami(
    filters=[
        {
            "name": "name",
            "values": ["debian-12-*"],
        },
        {
            "name": "architecture",
            "values": ["x86_64"],
        },
    ],
    owners=["136693071363"],  # Debian
    most_recent=True,
).id


class Node:
    """A base class for Solana aws nodes."""

    def __init__(self, name: str, config: Optional[pulumi.Config] = None):
        self.name = name

        self.config = config or pulumi.Config("node")

        self.ssh_key = tls.PrivateKey(self.n("ssh-key"), algorithm="ED25519")
        self.key_pair = aws.ec2.KeyPair(
            self.n("keypair"), public_key=self.ssh_key.public_key_openssh
        )

        self.instance: aws.ec2.Instance
        self.connection: "svmkit.ssh.ConnectionArgsDict"

    def n(self, s: str) -> str:
        return f"{self.name}-{s}"


class FaucetNode(Node):
    """A Solana Faucet node."""

    def __init__(self, name, config: Optional[pulumi.Config] = None):
        super().__init__(name, config)

        self.faucet_key = svmkit.KeyPair("faucet-key")
        self.treasury_key = svmkit.KeyPair("treasury-key")
        self.stake_account_key = svmkit.KeyPair("stake-account-key")

        self.instance = aws.ec2.Instance(
            self.n("instance"),
            ami=ami,
            instance_type="t3.xlarge",
            key_name=self.key_pair.key_name,
            vpc_security_group_ids=[external_sg.id, internal_sg.id],
            tags={
                "Name": pulumi.get_stack() + "-" + self.name,
            },
        )

        self.connection = svmkit.ssh.ConnectionArgsDict(
            {
                "host": self.instance.public_dns,
                "user": "admin",
                "private_key": self.ssh_key.private_key_openssh,
            }
        )

    def configure_faucet(self, depends_on=[]) -> svmkit.faucet.Faucet:
        return svmkit.faucet.Faucet(
            f"{self.name}-faucet",
            connection=self.connection,
            keypair=self.faucet_key.json,
            flags={
                "per_request_cap": 1000,
            },
            opts=pulumi.ResourceOptions(depends_on=([self.instance] + depends_on)),
        )


class ValidatorNode(Node):
    """An Solana Validator node."""

    def __init__(
        self,
        name,
        config: Optional[pulumi.Config],
        rpc_port: int = 8899,
        gossip_port: int = 8001,
    ):
        super().__init__(name, config)
        self.rpc_port = rpc_port
        self.gossip_port = gossip_port

        self.validator_key = svmkit.KeyPair(self.n("validator-key"))
        self.vote_account_key = svmkit.KeyPair(self.n("vote-account-key"))

        instance_type = self.config.get("instanceType") or "c6i.xlarge"
        iops = self.config.get_int("volumeIOPS") or 5000

        self.instance = aws.ec2.Instance(
            self.n("instance"),
            ami=ami,
            instance_type=instance_type,
            key_name=self.key_pair.key_name,
            vpc_security_group_ids=[external_sg.id, internal_sg.id],
            ebs_block_devices=[
                {
                    "device_name": "/dev/sdf",
                    "volume_size": 100,
                    "volume_type": "gp3",
                    "iops": iops,
                },
                {
                    "device_name": "/dev/sdg",
                    "volume_size": 204,
                    "volume_type": "gp3",
                    "iops": iops,
                },
            ],
            user_data="""#!/bin/bash
mkfs -t ext4 /dev/sdf
mkfs -t ext4 /dev/sdg
mkdir -p /home/sol/accounts
mkdir -p /home/sol/ledger
cat <<EOF >> /etc/fstab
/dev/sdf	/home/sol/accounts	ext4	defaults	0	0
/dev/sdg	/home/sol/ledger	ext4	defaults	0	0
EOF
systemctl daemon-reload
mount -a
""",
            tags={
                "Name": pulumi.get_stack() + "-" + self.name,
            },
        )

        self.connection = svmkit.ssh.ConnectionArgsDict(
            {
                "host": self.instance.public_dns,
                "user": "admin",
                "private_key": self.ssh_key.private_key_openssh,
            }
        )

        self.base_flags = svmkit.agave.FlagsArgsDict(
            {
                "only_known_rpc": False,
                "rpc_port": self.rpc_port,
                "dynamic_port_range": "8002-8020",
                "private_rpc": False,
                "gossip_port": self.gossip_port,
                "rpc_bind_address": "0.0.0.0",
                "wal_recovery_mode": "skip_any_corrupted_record",
                "limit_ledger_size": 50000000,
                "block_production_method": "central-scheduler",
                "full_snapshot_interval_slots": 1000,
                "no_wait_for_vote_to_start_leader": True,
                "use_snapshot_archives_at_startup": "when-newest",
                "allow_private_addr": True,
            }
        )

    def get_validator_flags(self, new_flags) -> svmkit.agave.FlagsArgsDict:
        flags = self.base_flags.copy()
        flags.update(new_flags)
        return flags

    def configure_validator(
        self,
        flags: Union["svmkit.agave.FlagsArgs", "svmkit.agave.FlagsArgsDict"],
        environment: Union[
            "svmkit.solana.EnvironmentArgs", "svmkit.solana.EnvironmentArgsDict"
        ],
        startup_policy: Union[
            "svmkit.agave.StartupPolicyArgs", "svmkit.agave.StartupPolicyArgsDict"
        ],
        depends_on=[],
    ) -> svmkit.validator.Agave:
        return svmkit.validator.Agave(
            f"{self.name}-validator",
            environment=environment,
            connection=self.connection,
            version=AGAVE_VERSION,
            startup_policy=startup_policy,
            shutdown_policy={
                "force": True,
            },
            key_pairs={
                "identity": self.validator_key.json,
                "vote_account": self.vote_account_key.json,
            },
            flags=flags,
            timeout_config={
                "rpc_service_timeout": 120,
            },
            info={
                "name": self.name,
                "details": "An AWS network-based SPE validator node.",
            },
            opts=pulumi.ResourceOptions(depends_on=([self.instance] + depends_on)),
        )


class BootstrapNode(ValidatorNode):
    """An Solana Bootstrap node."""

    def __init__(
        self, name, config: Optional[pulumi.Config], rpc_port=8899, gossip_port=8001
    ):
        super().__init__(name, config, rpc_port, gossip_port)

        self.treasury_key = svmkit.KeyPair(self.n("treasury-key"))
        self.stake_account_key = svmkit.KeyPair(self.n("stake-account-key"))

    def configure_genesis(
        self, faucet_key: svmkit.KeyPair, depends_on=[]
    ) -> svmkit.genesis.Solana:
        genesis = svmkit.genesis.Solana(
            f"{self.name}-genesis",
            connection=self.connection,
            version=AGAVE_VERSION,
            flags={
                "ledger_path": "/home/sol/ledger",
                "identity_pubkey": self.validator_key.public_key,
                "vote_pubkey": self.vote_account_key.public_key,
                "stake_pubkey": self.stake_account_key.public_key,
                "faucet_pubkey": faucet_key.public_key,
            },
            primordial=[
                {
                    "pubkey": self.validator_key.public_key,
                    "lamports": "1000000000000",  # 1000 SOL
                },
                {
                    "pubkey": self.treasury_key.public_key,
                    "lamports": "100000000000000",  # 100000 SOL
                },
                {
                    "pubkey": faucet_key.public_key,
                    "lamports": "1000000000000",  # 1000 SOL
                },
            ],
            opts=pulumi.ResourceOptions(depends_on=([self.instance] + depends_on)),
        )

        return genesis
