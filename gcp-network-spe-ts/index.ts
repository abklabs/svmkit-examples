import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";
import { Node, agaveVersion } from "./spe";

const nodeConfig = new pulumi.Config("node");
const totalNodes = nodeConfig.getNumber("count") ?? 3;
const tunerConfig = new pulumi.Config("tuner");

const gossipPort = 8001;
const rpcPort = 8899;
const faucetPort = 9900;

const faucetKey = new svmkit.KeyPair("faucet-key");
const treasuryKey = new svmkit.KeyPair("treasury-key");
const stakeAccountKey = new svmkit.KeyPair("stake-account-key");

const bootstrapNode = new Node("bootstrap-node");

const runnerConfig = {};

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
    connection: bootstrapNode.connection,
    params: tunerParams,
  },
  {
    dependsOn: [bootstrapNode.instance],
  }
);

const genesis = new svmkit.genesis.Solana(
  "genesis",
  {
    connection: bootstrapNode.connection,
    version: agaveVersion,
    flags: {
      ledgerPath: "/home/sol/ledger",
      identityPubkey: bootstrapNode.validatorKey.publicKey,
      votePubkey: bootstrapNode.voteAccountKey.publicKey,
      stakePubkey: stakeAccountKey.publicKey,
      faucetPubkey: faucetKey.publicKey,
      bootstrapValidatorStakeLamports: 10000000000, // 10 SOL
      enableWarmupEpochs: true,
    },
    primordial: [
      {
        pubkey: bootstrapNode.validatorKey.publicKey,
        lamports: 1000000000000, // 1000 SOL
      },
      {
        pubkey: treasuryKey.publicKey,
        lamports: 100000000000000, // 100000 SOL
      },
      {
        pubkey: faucetKey.publicKey,
        lamports: 1000000000000, // 1000 SOL
      },
    ],
  },
  {
    dependsOn: [bootstrapNode.instance],
  }
);

const solEnv = {
  rpcURL: bootstrapNode.privateIP.apply((ip) => `http://${ip}:${rpcPort}`),
};

const rpcFaucetAddress = bootstrapNode.privateIP.apply(
  (ip) => `${ip}:${faucetPort}`
);

const baseFlags: svmkit.types.input.agave.FlagsArgs = {
  onlyKnownRPC: false,
  rpcPort,
  dynamicPortRange: "8002-8020",
  privateRPC: false,
  gossipPort,
  rpcBindAddress: "0.0.0.0",
  walRecoveryMode: "skip_any_corrupted_record",
  limitLedgerSize: 50000000,
  blockProductionMethod: "central-scheduler",
  fullSnapshotIntervalSlots: 1000,
  noWaitForVoteToStartLeader: true,
  useSnapshotArchivesAtStartup: "when-newest",
  allowPrivateAddr: true,
  rpcFaucetAddress,
};

const bootstrapFlags: svmkit.types.input.agave.FlagsArgs = {
  ...baseFlags,
  fullRpcAPI: true,
  noVoting: false,
  gossipHost: bootstrapNode.privateIP,
  enableExtendedTxMetadataStorage: true,
  enableRpcTransactionHistory: true,
};

const faucet = new svmkit.faucet.Faucet(
  "bootstrap-faucet",
  {
    connection: bootstrapNode.connection,
    keypair: faucetKey.json,
    flags: {
      perRequestCap: 1000,
    },
  },
  {
    dependsOn: [genesis],
  }
);

const bootstrapValidator = bootstrapNode.configureValidator(
  bootstrapFlags,
  solEnv,
  {
    waitForRPCHealth: true,
  },
  [faucet],
  runnerConfig
);

const nodes = [...Array(totalNodes - 1)].map((_, i) => new Node(`node${i}`));
const allNodes = [bootstrapNode, ...nodes];

nodes.forEach((node) => {
  const otherNodes = allNodes.filter((x) => x != node);
  const entryPoint = otherNodes.map((node) =>
    node.privateIP.apply((v) => `${v}:${gossipPort}`)
  );

  const tuner = new svmkit.tuner.Tuner(
    node.name + "-tuner",
    {
      connection: node.connection,
      params: tunerParams,
    },
    {
      dependsOn: [node.instance],
    }
  );

  const flags: svmkit.types.input.agave.FlagsArgs = {
    ...baseFlags,
    entryPoint,
    knownValidator: otherNodes.map((x) => x.validatorKey.publicKey),
    expectedGenesisHash: genesis.genesisHash,
    fullRpcAPI: node == bootstrapNode,
    gossipHost: node.privateIP,
  };

  node.configureValidator(
    flags,
    solEnv,
    {},
    [bootstrapValidator],
    runnerConfig
  );

  const transfer = new svmkit.account.Transfer(
    node.name + "-transfer",
    {
      connection: bootstrapNode.connection,
      transactionOptions: {
        keyPair: treasuryKey.json,
      },
      amount: 100,
      recipientPubkey: node.validatorKey.publicKey,
      allowUnfundedRecipient: true,
    },
    {
      dependsOn: [bootstrapValidator],
    }
  );
  const voteAccount = new svmkit.account.VoteAccount(
    node.name + "-voteAccount",
    {
      connection: bootstrapNode.connection,
      keyPairs: {
        identity: node.validatorKey.json,
        voteAccount: node.voteAccountKey.json,
        authWithdrawer: treasuryKey.json,
      },
    },
    {
      dependsOn: [transfer],
    }
  );

  const stakeAccountKey = new svmkit.KeyPair(node.name + "-stakeAccount-key");
  new svmkit.account.StakeAccount(
    node.name + "-stakeAccount",
    {
      connection: bootstrapNode.connection,

      transactionOptions: {
        keyPair: treasuryKey.json,
      },
      keyPairs: {
        stakeAccount: stakeAccountKey.json,
        voteAccount: node.voteAccountKey.json,
      },
      amount: 10,
    },
    {
      dependsOn: [voteAccount],
    }
  );
});

export const nodes_name = allNodes.map((x) => x.name);
export const nodes_public_ip = allNodes.map((x) => x.publicIP);
export const nodes_private_key = allNodes.map(
  (x) => x.sshKey.privateKeyOpenssh
);
export const speInfo = {
  treasuryKey: treasuryKey,
  bootstrap: {
    connection: bootstrapNode.connection,
  },
  otherValidators: nodes.map((node) => ({
    voteAccountKey: node.voteAccountKey,
  })),
};
