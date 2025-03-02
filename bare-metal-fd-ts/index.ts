import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";

import { basePaths, firedancerPaths } from "./paths";

const solanaConfig = new pulumi.Config("solana");
const remote = new pulumi.Config("remote");

// Lookup information about the Solana network.
const networkName =
  solanaConfig.get<svmkit.solana.NetworkName>("network") ??
  svmkit.solana.NetworkName.Testnet;
const networkInfo = svmkit.networkinfo.getNetworkInfoOutput({ networkName });

// Create some keys for this validator to use.
export const validatorKey = new svmkit.KeyPair("validator-key").json;
export const voteAccountKey = new svmkit.KeyPair("vote-account-key").json;
export const withdrawerKey = new svmkit.KeyPair("withdrawer-key").json;

// Point pulumi-svmkit at the configured machine's SSH connection.
const connection = {
  host: remote.require("host"),
  user: remote.require("user"),
  privateKey: remote.requireSecret("privateKey"),
};

// Instantiate a new Firedancer instance on the machine.
new svmkit.validator.Firedancer(
  "fd",
  {
    connection,
    paths: firedancerPaths,
    keyPairs: {
      identity: validatorKey,
      voteAccount: voteAccountKey,
    },
    config: {
      user: "sol",
      gossip: {
        host: connection.host,
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
    },
  },
);

// Expose information required to SSH to the validator host.
export const nodes_name = ["instance"];
export const nodes_public_ip = [connection.host];
export const nodes_user = [connection.user];
export const nodes_private_key = [connection.privateKey];
export const paths = {
  base: basePaths,
  firedancer: firedancerPaths,
};
