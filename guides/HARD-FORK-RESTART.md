# Hard Fork Restart

This guide provides step-by-step instructions on how to perform a hard fork in an SVM network when the cluster cannot achieve consensus due to an insufficient number of validator participation.

## Understanding consensus

Consensus is defined as at least 2/3 (66.67%) of the total stake agreeing on a fork.

For 3 nodes with equal stake, each validator has:

100% / 3 = 33.33%

When one validator fails, the remaining two hold:

33.33% + 33.33% = 66.66%

which is 0.01% short of consensus, and thus halts the cluster.

## Scenario: 3-Node Cluster Failure

```
$ solana validators

Identity                                      Vote Account                            Commission  Last Vote  Root Slot  Active Stake
2wZXe6ZTaeq9sZ5TdjYNKCxLeEZjioFQ8fwkyuzt4RBB  9cSatxfzU33mmjA6AwuXkqmiH3gxxa65cRqqh9X7uVuB  100%    4343       4312       9.999999344 SOL (33.33%)
HfdV6f5SBZFSVn3y6yLubFc358BGH3jHYWpiQLpoB88E  2v7p2rkk1zdQLtGtfJn4zkXxLkiKGyW9NbCHak2nbErt  100%    4343       4312       9.999999344 SOL (33.33%)
3C4VnPXBbN1aStk9Lej2zpLVBwqKJAHHi1Y3dn5r7zCY  J15gWTa5aJWm3hFcRNSN1GfTckf2HbJrhZ81sWPT3j4X  100%    4343       4312       9.999999344 SOL (33.33%)
```

To simulate an outage stop any of the validators.

```
$ sudo systemctl stop svmkit-agave-validator.service
```

The stopped validator is marked as unknown. The remaining 2 validators will not reach consensus and voting halts.

```
$ solana validators

Stake By Version:
2.1.9   -    2 current validators (66.67%)
unknown -    1 current validators (33.33%)
```

## Performing a Hard Fork

Since the cluster cannot continue, a hard-fork restart is required.

1. Stop all validators

```
$ sudo systemctl stop svmkit-agave-validator.service
```

Confirm all validators have the same latest optimistic slot.

```
$ sudo -i -u sol
sol$ agave-ledger-tool -l ledger latest-optimistic-slots

...

Slot    Hash                                             Timestamp
32179    D8V3P4oy3Qhn8KNMVeEjEH83zbuuwqD8fZ28Nwn4jf7S     2025-02-05T12:31:00.042+00:00
```

2. Generate hard fork snapshot

Run the following command on each validator:

```
sol$ agave-ledger-tool create-snapshot 32179 --hard-fork 32179
[2025-02-06T15:29:15.367501348Z INFO  solana_runtime::snapshot_utils] Generating snapshot archive for slot 32179, kind: FullSnapshot
[2025-02-06T15:29:15.421767786Z INFO  solana_runtime::snapshot_utils] Successfully created /home/sol/ledger/snapshot-32179-H6gZU8dX2kji2G3F9xNzZTJDUmshppGEbe2ux3tsK4oi.tar.zst. slot: 32179, elapsed ms: 54, size: 441990
[2025-02-06T15:29:15.421827944Z INFO  solana_metrics::metrics] datapoint: archive-snapshot-package slot=32179i archive_format="TarZstd" duration_ms=54i full-snapshot-archive-size=441990i
Successfully created snapshot for slot 32179, hash 6spvWBo8JyYqtYM8qurjGyRz8M49Pe2bLwTF4k2wfZpF: /home/sol/ledger/snapshot-32179-H6gZU8dX2kji2G3F9xNzZTJDUmshppGEbe2ux3tsK4oi.tar.zst
Shred version: 65416
```

_The `--expected-bank-hash`is the one after the text `Successfully created snapshot for slot {SLOT}, hash {EXPECTED_BANK_HASH}:`_

3. Update flags on the validator.

```typescript
new svmkit.validator.Agave(
  "validator",
  {
    connection,
    keyPairs: {
      identity: validatorKey.json,
      voteAccount: voteAccountKey.json,
    },
    flags: {
      hardFork: [32179],
      expectedBankHash: "6spvWBo8JyYqtYM8qurjGyRz8M49Pe2bLwTF4k2wfZpF",
      expectedShredVersion: 65416,
      noSnapshotFetch: true,
    },
  },
  {
    dependsOn: [instance],
  }
);
```

5. Apply changes

```
pulumi up

     Type                       Name                          Plan        Info
     pulumi:pulumi:Stack        aws-network-spe-py-hard-fork              3 messages
 +-  ├─ svmkit:validator:Agave  bootstrap-node-validator      replace     [diff:]
 +-  ├─ svmkit:validator:Agave  node1-validator               replace     [diff:]
 +-  └─ svmkit:validator:Agave  node0-validator               replace     [diff:]

Resources:
    +-3 to replace
    36 unchanged
```

This will restart the validators with the flags needed to hard-fork the network.

4. Confirm block production is restored

Once supermajority (80% of active stake) is in agreement on the fork voting commences without additional intervention.

```
solana validators

Stake By Version:
2.1.9 -    3 current validators (100.00%)
```
