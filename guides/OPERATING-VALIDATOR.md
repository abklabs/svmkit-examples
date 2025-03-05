# Setting Up a Solana Validator for Staking

This guide shows how to convert an existing [non-voting Solana validator](https://github.com/abklabs/svmkit-examples/tree/main/aws-validator-agave-ts) into one that participates in network consensus with staking capabilities. We'll build on the AWS validator Agave TypeScript example from the svmkit-examples repository.

## Overview

This guide provides step-by-step instructions to enable voting and staking on your validator by:
1. Adding necessary keypairs for funding and staking
2. Creating and configuring vote and stake accounts
3. Enabling voting functionality
4. Setting up stake delegation

## Step-by-Step Implementation

### Step 1: Add Treasury and Stake Account Keypairs

Add these keypairs to your existing configuration:

```typescript
// Add a treasury key for funding validator operations
const treasuryKey = new svmkit.KeyPair("treasury-key");
// Create a keypair for stake account
const stakeAccountKey = new svmkit.KeyPair("stake-account-key");

// Export public keys for funding
export const treasuryPublicKey = treasuryKey.publicKey;
export const stakeAccountPublicKey = stakeAccountKey.publicKey;
```

Deploy this initial change to generate the keypairs:
```bash
pulumi up
```

### Step 2: Retrieve and Fund Account Addresses

Get the addresses that need funding:
```bash
pulumi stack output treasuryPublicKey
pulumi stack output validatorPublicKey
```

Fund both accounts before continuing:
- Fund the treasury address with at least 0.3 SOL (for creating stake account)
- Ensure the validator has at least 0.1 SOL (for vote account creation)

You can use [Solana faucets](https://solana.com/developers/guides/getstarted/solana-token-airdrop-and-faucets) for devnet testing.

### Step 3: Create Vote Account

After funding, add the vote account configuration:

```typescript
// Create vote account
const voteAccount = new svmkit.account.VoteAccount("validator-vote-account", {
  connection: connection,
  keyPairs: {
    identity: validatorKey.json,
    voteAccount: voteAccountKey.json,
    authWithdrawer: treasuryKey.json, // Treasury key as withdraw authority
  },
}, { dependsOn: [instance] });

// Export vote account public key
export const voteAccountPublicKey = voteAccountKey.publicKey;
```

### Step 4: Configure Stake Account

With the vote account defined, add the stake account setup:

```typescript
// Create and delegate stake account
const stakeAccount = new svmkit.account.StakeAccount("validator-stake-account", {
  connection: connection,
  transactionOptions: {
    keyPair: treasuryKey.json, // Treasury funds the stake account
  },
  keyPairs: {
    stakeAccount: stakeAccountKey.json,
    voteAccount: voteAccountKey.json, // Delegate to your vote account
  },
  amount: 0.2, // Stake amount in SOL - adjust based on available funds
}, { dependsOn: [voteAccount] });
```

### Step 5: Enable Voting on Validator

Find your Agave validator configuration and change `noVoting` from `true` to `false`:

```typescript
flags: {
  // Other flags remain unchanged
  noVoting: false, // Change from true to false to enable voting
}
```

### Step 6: Deploy Complete Configuration

Deploy all changes:
```bash
pulumi up
```

## Verifying Your Setup

After successful deployment, verify your configuration:

```bash
# Check validator balance
solana balance $(pulumi stack output validatorPublicKey)

# Verify vote account exists and is properly configured
solana vote-account $(pulumi stack output voteAccountPublicKey)

# Check stake account and delegation
solana stake-account $(pulumi stack output stakeAccountPublicKey)
```

## Conclusion

Your Solana validator is now ready to participate in consensus and can receive stake delegations. You've successfully converted a non-voting validator to an active network participant.