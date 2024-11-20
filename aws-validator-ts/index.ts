import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";

const solanaConfig = new pulumi.Config("solana");

// AWS-specific resources are created inside.
import { sshKey, instance } from "./aws";

// For any network choice, set some base validator flags.
const baseFlags = {
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
};

// Provide some default options for known Solana networks.
const networkOptions = {
  devnet: {
    environment: {
      rpcURL: "https://api.devnet.solana.com",
    },
    flags: {
      ...baseFlags,
      entryPoint: [
        "entrypoint.devnet.solana.com:8001",
        "entrypoint2.devnet.solana.com:8001",
        "entrypoint3.devnet.solana.com:8001",
        "entrypoint4.devnet.solana.com:8001",
        "entrypoint5.devnet.solana.com:8001",
      ],
      knownValidator: [
        "dv1ZAGvdsz5hHLwWXsVnM94hWf1pjbKVau1QVkaMJ92",
        "dv2eQHeP4RFrJZ6UeiZWoc3XTtmtZCUKxxCApCDcRNV",
        "dv4ACNkpYPcE3aKmYDqZm9G5EB3J4MRoeE7WNDRBVJB",
        "dv3qDFk1DTF36Z62bNvrCXe9sKATA6xvVy6A798xxAS",
      ],
      expectedGenesisHash: "EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG",
    },
  },
  testnet: {
    environment: {
      rpcURL: "https://api.testnet.solana.com",
    },
    flags: {
      ...baseFlags,
      entryPoint: [
        "entrypoint.testnet.solana.com:8001",
        "entrypoint2.testnet.solana.com:8001",
        "entrypoint3.testnet.solana.com:8001",
      ],
      knownValidator: [
        "5D1fNXzvv5NjV1ysLjirC4WY92RNsVH18vjmcszZd8on",
        "7XSY3MrYnK8vq693Rju17bbPkCN3Z7KvvfvJx4kdrsSY",
        "Ft5fbkqNa76vnsjYNwjDZUXoTWpP7VYm3mtsaQckQADN",
        "9QxCLckBiJc783jnMvXZubK4wH86Eqqvashtrwvcsgkv",
      ],
      expectedGenesisHash: "4uhcVJyU9pJkvQyS88uRDiswHXSCkY3zQawwpjk2NsNY",
    },
  },
};

type NetworkName = keyof typeof networkOptions;

function isValidName(name: string): name is NetworkName {
  return Object.prototype.hasOwnProperty.call(networkOptions, name);
}

const networkName = solanaConfig.get("network") ?? "devnet";

if (!isValidName(networkName)) {
  throw new Error(`unknown Solana network '${networkName}' specified!`);
}

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
    keyPairs: {
      identity: validatorKey.json,
      voteAccount: voteAccountKey.json,
    },
    ...networkOptions[networkName],
  },
  {
    dependsOn: [instance],
  },
);

// Expose information required to SSH to the validator host.
export const PUBLIC_DNS_NAME = instance.publicDns;
export const SSH_PRIVATE_KEY = sshKey.privateKeyOpenssh;
