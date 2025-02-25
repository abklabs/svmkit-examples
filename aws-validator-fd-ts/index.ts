import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";

const solanaConfig = new pulumi.Config("solana");
const tunerConfig = new pulumi.Config("tuner");

// AWS-specific resources are created inside.
import { sshKey, instance } from "./aws";

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
    params: tunerParams,
  },
  {
    dependsOn: [instance],
  }
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
    },
  },
  {
    dependsOn: [instance],
  },
);

// Expose information required to SSH to the validator host.
export const nodes_name = ["instance"];
export const nodes_public_ip = [instance.publicIp];
export const nodes_private_key = [sshKey.privateKeyOpenssh];
export const tuner_params = tunerParams;
