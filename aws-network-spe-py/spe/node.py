from typing import Union

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
import pulumi_svmkit as svmkit

from .network import external_sg, internal_sg, subnet_id

node_config = pulumi.Config("node")
validator_config = pulumi.Config("validator")

agave_version = validator_config.get('version') or '2.2.14-1'
instance_type = node_config.get('instanceType') or "c6i.xlarge"
user = node_config.get('user') or 'admin'

iops = node_config.get_int('volumeIOPS') or 5000
swap_size = node_config.get_int('swapSize') or 8
root_volume_size = (node_config.get_int('rootVolumeSize') or 32) + swap_size

ami = aws.ec2.get_ami(
    filters=[
        {
            "name": "name",
            "values": ["debian-12-*"],
        },
        {
            "name": "architecture",
            "values": [node_config.get('instanceArch') or 'x86_64'],
        },
    ],
    owners=["136693071363"],  # Debian
    most_recent=True,
).id


class Node:
    def __init__(self, name):
        self.name = name

        def _(s):
            return f"{self.name}-{s}"

        self.ssh_key = tls.PrivateKey(_("ssh-key"), algorithm="ED25519")
        self.key_pair = aws.ec2.KeyPair(
            _("keypair"), public_key=self.ssh_key.public_key_openssh)

        self.validator_key = svmkit.KeyPair(_("validator-key"))
        self.vote_account_key = svmkit.KeyPair(_("vote-account-key"))

        stack_name = pulumi.get_stack()

        self.instance = aws.ec2.Instance(
            _("instance"),
            ami=ami,
            instance_type=instance_type,
            key_name=self.key_pair.key_name,
            root_block_device={
                "volume_size": root_volume_size,
                "volume_type": "gp3",
                "iops": iops,
            },
            vpc_security_group_ids=[external_sg.id, internal_sg.id],
            subnet_id=subnet_id,
            associate_public_ip_address=True,
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
            user_data=f"""#!/bin/bash
# Format the /dev/sdf and /dev/sdg devices with the ext4 filesystem.
mkfs -t ext4 /dev/sdf
mkfs -t ext4 /dev/sdg

# Create directories for Solana accounts and ledger data.
mkdir -p /home/sol/accounts
mkdir -p /home/sol/ledger

# Append entries to /etc/fstab to mount the devices and swap at boot.
cat <<EOF >> /etc/fstab
/dev/sdf	/home/sol/accounts	ext4	defaults	0	0
/dev/sdg	/home/sol/ledger	ext4	defaults	0	0
/swapfile none swap sw 0 0
EOF

# Setup swap space
fallocate -l {swap_size}GiB /swapfile
chmod 600 /swapfile
mkswap /swapfile

# Reload systemd manager configuration and mount all filesystems.
systemctl daemon-reload
mount -a
swapon -a
""",
            tags={
                "Name": stack_name + "-" + self.name,
                "Stack": stack_name,
            }
        )

        self.connection = svmkit.ssh.ConnectionArgsDict({
            "host": self.instance.public_dns,
            "user": user,
            "private_key": self.ssh_key.private_key_openssh,
        })

        self.machine = svmkit.machine.Machine(
            f"{self.name}-machine",
            connection=self.connection,
            opts=pulumi.ResourceOptions(depends_on=[self.instance])
        )

    def configure_validator(self, flags: Union['svmkit.agave.FlagsArgs', 'svmkit.agave.FlagsArgsDict'], environment: Union['svmkit.solana.EnvironmentArgs', 'svmkit.solana.EnvironmentArgsDict'], startup_policy: Union['svmkit.agave.StartupPolicyArgs', 'svmkit.agave.StartupPolicyArgsDict'], depends_on=[]):
        return svmkit.validator.Agave(
            f"{self.name}-validator",
            environment=environment,
            runner_config=svmkit.runner.ConfigArgs(
                package_config=svmkit.deb.PackageConfigArgs(
                    additional=['svmkit-spl-token-cli'],
                ),
            ),
            connection=self.connection,
            version=agave_version,
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
            opts=pulumi.ResourceOptions(
                depends_on=([self.machine] + depends_on))
        )
