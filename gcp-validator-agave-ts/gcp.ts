import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import * as tls from "@pulumi/tls";

const nodeConfig = new pulumi.Config("node");
const machineType = nodeConfig.get("machineType") ?? "c4-standard-8";
const osImage = nodeConfig.get("osImage") ?? "debian-12";
const diskSize = nodeConfig.getNumber("diskSize") ?? 256;

export const sshKey = new tls.PrivateKey("ssh-key", {
  algorithm: "ED25519",
});

const network = new gcp.compute.Network("network", {
  autoCreateSubnetworks: false,
});

const subnet = new gcp.compute.Subnetwork("subnet", {
  ipCidrRange: "10.0.1.0/24",
  network: network.id,
});

const firewall = new gcp.compute.Firewall("firewall", {
  network: network.selfLink,
  allows: [
    {
      protocol: "tcp",
      ports: ["22", "8000-8020", "8899"],
    },
    {
      protocol: "udp",
      ports: ["8000-8020"],
    },
  ],
  direction: "INGRESS",
  sourceRanges: ["0.0.0.0/0"],
  targetTags: [],
});

export const instance = new gcp.compute.Instance(
  "instance",
  {
    machineType,
    bootDisk: {
      initializeParams: {
        image: osImage,
        size: diskSize,
      },
    },
    networkInterfaces: [
      {
        network: network.id,
        subnetwork: subnet.id,
        accessConfigs: [{}],
      },
    ],
    serviceAccount: {
      scopes: ["https://www.googleapis.com/auth/cloud-platform"],
    },
    allowStoppingForUpdate: true,
    tags: [],
    metadata: {
      "enable-oslogin": "false",
      "ssh-keys": sshKey.publicKeyOpenssh.apply((k) => `admin:${k}`),
    },
  },
  { dependsOn: firewall },
);
