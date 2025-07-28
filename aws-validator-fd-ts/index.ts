import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";

const firewallConfig = new pulumi.Config("firewall");
const solanaConfig = new pulumi.Config("solana");
const tunerConfig = new pulumi.Config("tuner");

// AWS-specific resources are created inside.
import { sshKey, instance, instanceUser } from "./aws";

// Lookup information about the Solana network
const networkName =
  solanaConfig.get<svmkit.solana.NetworkName>("network") ??
  svmkit.solana.NetworkName.Testnet;
const networkInfo = svmkit.networkinfo.getNetworkInfoOutput({ networkName });

// Create some keys for this validator to use.
export const validatorKey = new svmkit.KeyPair("validator-key").json;
export const voteAccountKey = new svmkit.KeyPair("vote-account-key").json;
export const withdrawerKey = new svmkit.KeyPair("withdrawer-key").json;

// Point pulumi-svmkit at the AWS EC2 instance's SSH connection.
const connection = {
  host: instance.publicDns,
  user: instanceUser,
  privateKey: sshKey.privateKeyOpenssh,
};

// Configure the instance for SVMKit
const machine = new svmkit.machine.Machine(
  "machine",
  {
    connection,
  },
  {
    dependsOn: [instance],
  },
);

// Firewall setup
const firewallVariant =
  firewallConfig.get<svmkit.firewall.FirewallVariant>("variant") ??
  svmkit.firewall.FirewallVariant.Generic;

// Retrieve the default firewall parameters for that variant
const genericFirewallParamsOutput =
  svmkit.firewall.getDefaultFirewallParamsOutput({
    variant: firewallVariant,
  });

// "Apply" those params so we can pass them to the Firewall constructor
const firewallParams = genericFirewallParamsOutput.apply((f) => ({
  allowPorts: [
    ...(f.allowPorts ?? []),
    "8000:8020/tcp",
    "8000:8020/udp",
    "8899",
    "8900/tcp",
    "8900:8915/udp",
  ],
}));

// Create the Firewall resource on the EC2 instance
const _firewall = new svmkit.firewall.Firewall(
  "firewall",
  {
    connection,
    params: firewallParams,
  },
  {
    dependsOn: [machine],
  },
);

// Tuner setup
const tunerVariant =
  tunerConfig.get<svmkit.tuner.TunerVariant>("variant") ??
  svmkit.tuner.TunerVariant.Generic;

// Retrieve the default tuner parameters for that variant
const genericTunerParamsOutput = svmkit.tuner.getDefaultTunerParamsOutput({
  variant: tunerVariant,
});

// "Apply" those params so we can pass them to the Tuner constructor
const tunerParams = genericTunerParamsOutput.apply((p) => ({
  cpuGovernor: p.cpuGovernor,
  kernel: p.kernel,
  net: p.net,
  vm: p.vm,
  fs: p.fs,
}));

// Create the Tuner resource on the EC2 instance
const _tuner = new svmkit.tuner.Tuner(
  "tuner",
  {
    connection,
    params: tunerParams,
  },
  {
    dependsOn: [machine],
  },
);

// Instantiate a new Firedancer instance on the machine.
new svmkit.validator.Firedancer(
  "fd",
  {
    connection,
    keyPairs: {
      identity: validatorKey,
      voteAccount: voteAccountKey,
    },
    config: {
      user: "sol",
      gossip: {
        host: instance.publicIp,
        entrypoints: networkInfo.entryPoint,
      },
      consensus: {
        identityPath: "/home/sol/validator-keypair.json",
        voteAccountPath: "/home/sol/vote-account-keypair.json",
        knownValidators: networkInfo.knownValidator,
        expectedGenesisHash: networkInfo.genesisHash,
      },
      ledger: {
        path: "/home/sol/ledger",
        accountsPath: "/home/sol/accounts",
      },
      rpc: {
        port: 8899,
        private: true,
      },
      log: {
        path: "-",
      },
    },
  },
  {
    dependsOn: [machine],
  },
);

// Expose information required to SSH to the validator host.
export const nodes = [
  {
    name: "instance",
    connection,
  },
];
export const tuner_params = tunerParams;
