import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";

const solanaConfig = new pulumi.Config("solana");

// AWS-specific resources are created inside.
import { sshKey, instance } from "./aws";

// Lookup information about the Solana network.
const networkName =
  solanaConfig.get<svmkit.solana.NetworkName>("network") ??
  svmkit.solana.NetworkName.Testnet;
const networkInfo = svmkit.networkinfo.getNetworkInfoOutput({ networkName });

// Create some keys for this validator to use.
const validatorKey = new svmkit.KeyPair("validator-key");
const voteAccountKey = new svmkit.KeyPair("vote-account-key");

// Point pulumi-svmkit at the AWS EC2 instance's SSH connection.
const connection = {
  host: instance.publicDns,
  user: "admin",
  privateKey: sshKey.privateKeyOpenssh,
};

// Instantiate a new Agave instance on the machine.
new svmkit.validator.Agave(
  "validator",
  {
    connection,
    version: "2.0.15-1",
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
    dependsOn: [instance],
  },
);

// Expose information required to SSH to the validator host.
export const PUBLIC_DNS_NAME = instance.publicDns;
export const SSH_PRIVATE_KEY = sshKey.privateKeyOpenssh;
