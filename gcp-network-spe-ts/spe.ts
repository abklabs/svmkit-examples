import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import * as tls from "@pulumi/tls";
import * as svmkit from "@svmkit/pulumi-svmkit";

const validatorConfig = new pulumi.Config("validator");

export const agaveVersion = validatorConfig.get("version") ?? "1.18.26-1";

const nodeConfig = new pulumi.Config("node");

const network = new gcp.compute.Network("network", {
  autoCreateSubnetworks: false,
});

const subnet = new gcp.compute.Subnetwork("subnet", {
  ipCidrRange: "10.0.1.0/24",
  network: network.id,
});

const firewalls = [
  new gcp.compute.Firewall("external", {
    network: network.selfLink,
    allows: [
      {
        protocol: "tcp",
        ports: ["22"],
      },
    ],
    direction: "INGRESS",
    sourceRanges: ["0.0.0.0/0"],
    targetTags: [],
  }),
  new gcp.compute.Firewall("internal", {
    network: network.selfLink,
    allows: [
      {
        protocol: "icmp",
      },
      {
        protocol: "tcp",
        ports: ["22", "8000-8020", "8899", "8900"],
      },
      {
        protocol: "udp",
        ports: ["8000-8020"],
      },
    ],
    sourceRanges: [subnet.ipCidrRange],
    targetTags: [],
  }),
];

export class Node {
  name: string;
  sshKey: tls.PrivateKey;
  validatorKey: svmkit.KeyPair;
  voteAccountKey: svmkit.KeyPair;
  instance: gcp.compute.Instance;
  publicIP: pulumi.Output<string>;
  privateIP: pulumi.Output<string>;
  connection: svmkit.types.input.ssh.ConnectionArgs;
  constructor(name: string) {
    this.name = name;

    const _ = (s: string) => `${this.name}-${s}`;

    this.sshKey = new tls.PrivateKey(_("ssh-key"), { algorithm: "ED25519" });
    this.validatorKey = new svmkit.KeyPair(_("validator-key"));
    this.voteAccountKey = new svmkit.KeyPair(_("vote-account-key"));

    const machineType = nodeConfig.get("machineType") || "n1-standard-4";
    const osImage = nodeConfig.get("osImage") || "debian-12";
    const diskSize = nodeConfig.getNumber("diskSize") || 64;

    this.instance = new gcp.compute.Instance(
      _("instance"),
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
          "ssh-keys": this.sshKey.publicKeyOpenssh.apply((k) => `admin:${k}`),
        },
      },
      { dependsOn: firewalls },
    );

    this.publicIP = this.instance.networkInterfaces.apply((interfaces) => {
      return interfaces[0].accessConfigs![0].natIp;
    });

    this.privateIP = this.instance.networkInterfaces.apply((interfaces) => {
      return interfaces[0].networkIp;
    });

    this.connection = {
      host: this.publicIP,
      user: "admin",
      privateKey: this.sshKey.privateKeyOpenssh,
    };
  }

  configureValidator(
    flags: svmkit.types.input.agave.FlagsArgs,
    environment: svmkit.types.input.solana.EnvironmentArgs,
    startupPolicy: svmkit.types.input.agave.StartupPolicyArgs,
    dependsOn: pulumi.Input<pulumi.Resource>[],
    runnerConfig?: pulumi.Input<svmkit.types.input.runner.ConfigArgs>,
  ) {
    return new svmkit.validator.Agave(
      `${this.name}-validator`,
      {
        environment,
        runnerConfig,
        connection: this.connection,
        version: agaveVersion,
        startupPolicy,
        shutdownPolicy: {
          force: true,
        },
        keyPairs: {
          identity: this.validatorKey.json,
          voteAccount: this.voteAccountKey.json,
        },
        flags,
        timeoutConfig: {
          rpcServiceTimeout: 120,
        },
        info: {
          name: this.name,
          details: "An AWS network-based SPE validator node.",
        },
      },
      {
        dependsOn: [this.instance, ...dependsOn],
      },
    );
  }
}
