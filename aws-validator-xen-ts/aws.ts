import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as tls from "@pulumi/tls";

const nodeConfig = new pulumi.Config("node");
const instanceType = nodeConfig.get("instanceType") ?? "t3.2xlarge";
const instanceArch = nodeConfig.get("instanceArch") ?? "x86_64";

// Setup a local SSH private key, stored inside Pulumi.
export const sshKey = new tls.PrivateKey("ssh-key", {
  algorithm: "ED25519",
});

const keyPair = new aws.ec2.KeyPair("keypair", {
  publicKey: sshKey.publicKeyOpenssh,
});

// Get AMI information on the latest Debian image inside AWS.
const ami = pulumi.output(
  aws.ec2.getAmi({
    filters: [
      {
        name: "name",
        values: ["debian-12-*"],
      },
      {
        name: "architecture",
        values: [instanceArch],
      },
    ],
    owners: ["136693071363"], // Debian
    mostRecent: true,
  })
).id;

const securityGroup = new aws.ec2.SecurityGroup("security-group", {
  description: "Allow SSH and specific inbound traffic",
  ingress: [
    {
      protocol: "tcp",
      fromPort: 22,
      toPort: 22,
      cidrBlocks: ["0.0.0.0/0"],
    },
    {
      protocol: "tcp",
      fromPort: 8000,
      toPort: 8020,
      cidrBlocks: ["0.0.0.0/0"],
    },
    {
      protocol: "udp",
      fromPort: 8000,
      toPort: 8020,
      cidrBlocks: ["0.0.0.0/0"],
    },
  ],
  egress: [
    {
      protocol: "-1",
      fromPort: 0,
      toPort: 0,
      cidrBlocks: ["0.0.0.0/0"],
    },
  ],
});

export const instance = new aws.ec2.Instance("instance", {
  ami,
  instanceType,
  keyName: keyPair.keyName,
  vpcSecurityGroupIds: [securityGroup.id],
  ebsBlockDevices: [
    {
      deviceName: "/dev/sdf",
      volumeSize: 100,
      volumeType: "io2",
      iops: 16000,
    },
    {
      deviceName: "/dev/sdg",
      volumeSize: 500,
      volumeType: "io2",
      iops: 16000,
    },
  ],
  userData: `#!/bin/bash
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
`,
  tags: {
    Name: `${pulumi.getStack()}-validator`,
    Stack: pulumi.getStack(),
  },
});
