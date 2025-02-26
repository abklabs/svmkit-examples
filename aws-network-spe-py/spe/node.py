from typing import Union

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
import pulumi_svmkit as svmkit

from .network import external_sg, internal_sg

AGAVE_VERSION = "1.18.26-1"

node_config = pulumi.Config("node")

volume_iops = node_config.get_int("volumeIOPS") or 5000

stack_name = pulumi.get_stack()

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


class Node(pulumi.ComponentResource):
    def __init__(self, name: str, instance_type: str, iops: int = volume_iops, root_volume_size: int = 20, swap_size: int = 8192, opts=None) -> None:
        super().__init__('svmkit-examples:aws:Node', name, None, opts)

        self.name = name

        def _(s):
            return f"{self.name}-{s}"

        self.ssh_key = tls.PrivateKey(
            _("ssh-key"), algorithm="ED25519", opts=pulumi.ResourceOptions(parent=self))
        self.key_pair = aws.ec2.KeyPair(
            _("keypair"), public_key=self.ssh_key.public_key_openssh, opts=pulumi.ResourceOptions(parent=self))

        self.validator_key = svmkit.KeyPair(
            _("validator-key"), opts=pulumi.ResourceOptions(parent=self))
        self.vote_account_key = svmkit.KeyPair(
            _("vote-account-key"), opts=pulumi.ResourceOptions(parent=self))

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
fallocate -l {swap_size}M /swapfile
chmod 600 /swapfile
mkswap /swapfile

# Reload systemd manager configuration and mount all filesystems.
systemctl daemon-reload
mount -a
swapon -a
""",
            tags={
                "Name": stack_name + "-" + name,
                "Stack": stack_name,
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.connection = svmkit.ssh.ConnectionArgsDict({
            "host": self.instance.public_dns,
            "user": "admin",
            "private_key": self.ssh_key.private_key_openssh,
        })

        self.register_outputs({
            "ssh_key": self.ssh_key,
            "key_pair": self.key_pair,
            "validator_key": self.validator_key,
            "vote_account_key": self.vote_account_key,
            "instance": self.instance,
            "connection": self.connection,
        })
