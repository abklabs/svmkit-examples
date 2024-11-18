from typing import Union

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
import pulumi_svmkit as svmkit

from .network import external_sg, internal_sg

node_config = pulumi.Config("node")

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

agave_version = "1.18.24-1"


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

        instance_type = node_config.get('instanceType') or "c6i.xlarge"
        iops = node_config.get_int('volumeIOPS') or 5000
        self.instance = aws.ec2.Instance(
            _("instance"),
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
"""
        )

        self.connection = svmkit.ssh.ConnectionArgsDict({
            "host": self.instance.public_dns,
            "user": "admin",
            "private_key": self.ssh_key.private_key_openssh
        })

    def configure_validator(self, flags: Union['svmkit.agave.FlagsArgs', 'svmkit.agave.FlagsArgsDict'], environment: Union['svmkit.solana.EnvironmentArgs', 'svmkit.solana.EnvironmentArgsDict'],  depends_on=[]):
        return svmkit.validator.Agave(
            f"{self.name}-validator",
            environment=environment,
            connection=self.connection,
            version=agave_version,
            key_pairs={
                "identity": self.validator_key.json,
                "vote_account": self.vote_account_key.json,
            },
            flags=flags,
            opts=pulumi.ResourceOptions(
                depends_on=([self.instance] + depends_on))
        )
