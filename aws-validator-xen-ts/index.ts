import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";

const tunerConfig = new pulumi.Config("tuner");

// AWS-specific resources are created inside.
import { sshKey, instance } from "./aws";

import { basePaths, tunerPaths, agavePaths } from "./paths";

// Create some keys for this validator to use.
const validatorKey = new svmkit.KeyPair("validator-key");
const voteAccountKey = new svmkit.KeyPair("vote-account-key");

// Point pulumi-svmkit at the AWS EC2 instance's SSH connection.
const connection = {
  host: instance.publicDns,
  user: "admin",
  privateKey: sshKey.privateKeyOpenssh,
};

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
    paths: tunerPaths,
    params: tunerParams,
  },
  {
    dependsOn: [instance],
  }
);

// Instantiate a new Xen instance on the machine.
new svmkit.validator.Agave(
  "validator",
  {
    connection,
    paths: agavePaths,
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
    dependsOn: [instance],
  }
);

// Expose information required to SSH to the validator host.
export const nodes_name = ["instance"];
export const nodes_public_ip = [instance.publicIp];
export const nodes_private_key = [sshKey.privateKeyOpenssh];
export const tuner_params = tunerParams;
export const paths = {
  base: basePaths,
  tuner: tunerPaths,
  agave: agavePaths,
};
