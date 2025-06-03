import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";

const validatorConfig = new pulumi.Config("validator");
const solanaConfig = new pulumi.Config("solana");
const firewallConfig = new pulumi.Config("firewall");
const tunerConfig = new pulumi.Config("tuner");

// AWS-specific resources are created inside.
import { sshKey, instance, user } from "./gcp";

// Lookup information about the Solana network.
const networkName =
  solanaConfig.get<svmkit.solana.NetworkName>("network") ??
  svmkit.solana.NetworkName.Testnet;
const networkInfo = svmkit.networkinfo.getNetworkInfoOutput({ networkName });
const agaveVersion = validatorConfig.get("version") ?? "2.2.14-1";

// Create some keys for this validator to use.
const validatorKey = new svmkit.KeyPair("validator-key");
const voteAccountKey = new svmkit.KeyPair("vote-account-key");

const instanceIP = instance.networkInterfaces.apply((interfaces) => {
  return interfaces[0].accessConfigs![0].natIp;
});

// Point pulumi-svmkit at the AWS EC2 instance's SSH connection.
const connection = {
  host: instanceIP,
  user,
  privateKey: sshKey.privateKeyOpenssh,
  dialErrorLimit: 50,
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
  ],
}));

// Create the Firewall resource on the EC2 instance
const firewall = new svmkit.firewall.Firewall(
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
const tuner = new svmkit.tuner.Tuner(
  "tuner",
  {
    connection,
    params: tunerParams,
  },
  {
    dependsOn: [machine],
  },
);

// Instantiate a new Agave instance on the machine.
new svmkit.validator.Agave(
  "validator",
  {
    connection,
    version: agaveVersion,
    environment: {
      rpcURL: networkInfo.rpcURL[0],
    },
    keyPairs: {
      identity: validatorKey.json,
      voteAccount: voteAccountKey.json,
    },
    flags: {
      useSnapshotArchivesAtStartup: "when-newest",
      fullRpcAPI: false,
      rpcPort: 8899,
      privateRPC: true,
      onlyKnownRPC: true,
      dynamicPortRange: "8002-8020",
      gossipHost: instanceIP,
      gossipPort: 8001,
      rpcBindAddress: "0.0.0.0",
      walRecoveryMode: "skip_any_corrupted_record",
      limitLedgerSize: 50000000,
      blockProductionMethod: "central-scheduler",
      fullSnapshotIntervalSlots: 1000,
      noWaitForVoteToStartLeader: true,
      noVoting: true,
      entryPoint: networkInfo.entryPoint,
      knownValidator: networkInfo.knownValidator,
      expectedGenesisHash: networkInfo.genesisHash,
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
