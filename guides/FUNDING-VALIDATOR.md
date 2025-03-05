# Setting Up a Solana Validator with Pulumi and TypeScript

## Introduction

This guide will walk you through enhancing your existing Solana validator setup with additional functionality using Pulumi and TypeScript. Specifically, we'll focus on funding your validator identity and creating vote and stake accounts.

## Prerequisites

- Existing Pulumi TypeScript project for Solana validator setup
- Basic understanding of Solana validators
- Familiarity with TypeScript and Pulumi
- Necessary access to fund accounts

## Process Overview

We'll add the following components to your existing setup:

1. Create a treasury keypair for funding
2. Fund the validator identity
3. Create a vote account
4. Create a stake account
5. Export public keys as Pulumi outputs

## Existing Setup

Your current setup already includes:
- AWS infrastructure (EC2 instance, SSH key)
- Network configuration
- Validator and vote account keypairs
- Validator tuning configuration
- Agave validator installation

## Implementation

Let's enhance your existing `index.ts` file with the additional components. Here's where to add the new code:

### 1. Add a Treasury Keypair

After your validator and vote account keypair definitions, add:

```typescript
// Add a treasury key for funding validator operations
const treasuryKey = new svmkit.KeyPair("treasury-key");

// Export the treasury public key so you can fund it externally
export const treasuryPublicKey = treasuryKey.publicKey;
```

### 2. Fund the Validator Identity

After the Agave validator configuration, add:

```typescript
// Fund the validator identity from treasury
// NOTE: You need to first externally fund the treasury keypair
const validatorFunding = new svmkit.account.Transfer("validator-funding", {
    connection: {
        clusterUrl: networkInfo.rpcURL[0],
        commitment: "confirmed",
    },
    transactionOptions: {
        keyPair: treasuryKey.json,
    },
    amount: 100, // Amount in SOL
    recipientPubkey: validatorKey.publicKey,
    allowUnfundedRecipient: true,
});
```

### 3. Create Vote Account

Update your code to create the vote account explicitly:

```typescript
// Create vote account
const voteAccount = new svmkit.account.VoteAccount("validator-vote-account", {
    connection: {
        clusterUrl: networkInfo.rpcURL[0],
        commitment: "confirmed",
    },
    keyPairs: {
        identity: validatorKey.json,
        voteAccount: voteAccountKey.json,
        authWithdrawer: treasuryKey.json, // Treasury key as the withdraw authority
    },
    commission: 10, // 10% commission, adjust as needed
}, { dependsOn: [validatorFunding] });

// Export vote account public key
export const voteAccountPublicKey = voteAccountKey.publicKey;
```

### 4. Create Stake Account

Finally, add the stake account setup:

```typescript
// Create stake account key
const stakeAccountKey = new svmkit.KeyPair("stake-account-key");

// Create and delegate stake account
const stakeAccount = new svmkit.account.StakeAccount("validator-stake-account", {
    connection: {
        clusterUrl: networkInfo.rpcURL[0],
        commitment: "confirmed",
    },
    transactionOptions: {
        keyPair: treasuryKey.json,
    },
    keyPairs: {
        stakeAccount: stakeAccountKey.json,
        voteAccount: voteAccountKey.json,
    },
    amount: 10, // Stake amount in SOL
}, { dependsOn: [voteAccount] });

// Export stake account public key
export const stakeAccountPublicKey = stakeAccountKey.publicKey;
```

## Complete Enhanced Code

Here's the complete `index.ts` file with all the additions (new sections are commented):

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as svmkit from "@svmkit/pulumi-svmkit";
const solanaConfig = new pulumi.Config("solana");
const tunerConfig = new pulumi.Config("tuner");
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

// **NEW CODE: Create a treasury key for funding**
const treasuryKey = new svmkit.KeyPair("treasury-key");

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
// Instantiate a new Agave instance on the machine.
new svmkit.validator.Agave(
  "validator",
  {
    connection,
    version: "2.1.13-1",
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

// **NEW CODE: Fund the validator identity**
const validatorFunding = new svmkit.account.Transfer("validator-funding", {
    connection: {
        clusterUrl: networkInfo.rpcURL[0],
        commitment: "confirmed",
    },
    transactionOptions: {
        keyPair: treasuryKey.json,
    },
    amount: 100, // Amount in SOL
    recipientPubkey: validatorKey.publicKey,
    allowUnfundedRecipient: true,
});

// **NEW CODE: Create vote account**
const voteAccount = new svmkit.account.VoteAccount("validator-vote-account", {
    connection: {
        clusterUrl: networkInfo.rpcURL[0],
        commitment: "confirmed",
    },
    keyPairs: {
        identity: validatorKey.json,
        voteAccount: voteAccountKey.json,
        authWithdrawer: treasuryKey.json,
    },
    commission: 10, // 10% commission, adjust as needed
}, { dependsOn: [validatorFunding] });

// **NEW CODE: Create stake account**
const stakeAccountKey = new svmkit.KeyPair("stake-account-key");
const stakeAccount = new svmkit.account.StakeAccount("validator-stake-account", {
    connection: {
        clusterUrl: networkInfo.rpcURL[0],
        commitment: "confirmed",
    },
    transactionOptions: {
        keyPair: treasuryKey.json,
    },
    keyPairs: {
        stakeAccount: stakeAccountKey.json,
        voteAccount: voteAccountKey.json,
    },
    amount: 10, // Stake amount in SOL
}, { dependsOn: [voteAccount] });

// Expose information required to SSH to the validator host.
export const nodes_name = ["instance"];
export const nodes_public_ip = [instance.publicIp];
export const nodes_private_key = [sshKey.privateKeyOpenssh];
export const tuner_params = tunerParams;

// **NEW CODE: Export key information**
export const treasuryPublicKey = treasuryKey.publicKey;
export const validatorPublicKey = validatorKey.publicKey;
export const voteAccountPublicKey = voteAccountKey.publicKey;
export const stakeAccountPublicKey = stakeAccountKey.publicKey;
```

## Treasury Funding Process

When setting up your validator, funding the treasury keypair requires a two-stage deployment process:

### Two-Stage Deployment

1. **Stage 1: Deploy Only the Treasury Keypair**
   
   Initially modify your code to only create and export the treasury keypair:

   ```typescript
   // Create a treasury key for funding
   const treasuryKey = new svmkit.KeyPair("treasury-key");

   // Export the treasury public key
   export const treasuryPublicKey = treasuryKey.publicKey;
   ```

   Deploy this simplified setup:
   ```bash
   pulumi up
   ```

   After deployment, retrieve the treasury public key:
   ```bash
   pulumi stack output treasuryPublicKey
   ```

   Fund this treasury address using an external wallet or faucet with enough SOL for both the validator identity transfer (100 SOL) and stake account creation (10 SOL).

2. **Stage 2: Deploy the Complete Setup**
   
   Once the treasury is funded, update your code to include all the transfer and stake account creation components, then run:
   ```bash
   pulumi up
   ```

This two-stage process is necessary because you need to know the treasury public key to fund it, but that key is only generated during the Pulumi deployment.

2. **Network Configuration**: The code automatically uses the network configuration you already have set up, whether it's testnet, devnet, or mainnet.

3. **Commission Setting**: Adjust the vote account commission based on your validator strategy. The example uses 10%.

4. **Stake Amount**: The stake account is created with 10 SOL in this example. Adjust this based on your needs and available funds.

## Deployment

To deploy the enhanced configuration:

```bash
pulumi up
```

This will show you a preview of the new resources to be created. Confirm to create them.

## Monitoring

After deployment, you can check the status of your accounts:

```bash
# Check validator balance
solana balance $(pulumi stack output validatorPublicKey)

# Check vote account
solana vote-account $(pulumi stack output voteAccountPublicKey)

# Check stake account
solana stake-account $(pulumi stack output stakeAccountPublicKey)
```

## Conclusion

By enhancing your existing Solana validator setup with funding, vote account, and stake account creation, you've completed the full validator deployment process. This allows your validator to participate in the Solana network consensus and potentially earn rewards.

Remember to monitor your validator's performance and adjust stake amounts or commission as needed. Regular updates to the Solana software are also important to maintain compatibility with the network.