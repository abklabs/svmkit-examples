import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";

const firewallConfig = new pulumi.Config("firewall");
const tunerConfig = new pulumi.Config("tuner");

// AWS-specific resources are created inside.
import { sshKey, instance, instanceUser } from "./aws";

// Create some keys for this validator to use.
const validatorKey = new svmkit.KeyPair("validator-key");
const voteAccountKey = new svmkit.KeyPair("vote-account-key");

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

// Instantiate a new Xen instance on the machine.
new svmkit.validator.Agave(
  "validator",
  {
    connection,
    variant: "tachyon",
    environment: {
      rpcURL: "https://rpc.testnet.x1.xyz",
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
      gossipPort: 8001,
      rpcBindAddress: "0.0.0.0",
      walRecoveryMode: "skip_any_corrupted_record",
      limitLedgerSize: 50000000,
      blockProductionMethod: "central-scheduler",
      fullSnapshotIntervalSlots: 5000,
      noWaitForVoteToStartLeader: true,
      noVoting: true,
      maximumIncrementalSnapshotsToRetain: 10,
      maximumFullSnapshotsToRetain: 50,
      enableRpcTransactionHistory: true,
      enableExtendedTxMetadataStorage: true,
      rpcPubsubEnableBlockSubscription: true,
      entryPoint: [
        "entrypoint1.testnet.x1.xyz:8001",
        "entrypoint2.testnet.x1.xyz:8000",
        "entrypoint3.testnet.x1.xyz:8000",
      ],
      knownValidator: [
        "Abt4r6uhFs7yPwR3jT5qbnLjBtasgHkRVAd1W6H5yonT",
        "5NfpgFCwrYzcgJkda9bRJvccycLUo3dvVQsVAK2W43Um",
        "FcrZRBfVk2h634L9yvkysJdmvdAprq1NM4u263NuR6LC",
      ],
      expectedGenesisHash: "C7ucgdDEhxLTpXHhWSZxavSVmaNTUJWwT5iTdeaviDho",
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
