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

The stopped validator is marked as unknown. The remaining 2 validators will not reach consensus and voting halts. Note that this guide assumes equally distributed stake. If you have just deployed the cluster, please wait until all stake is activated. This will take several hours and is dependent on the `slots_per_epoch` configured at genesis.

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

2. Install the ledger tool (if not already installed)

The agave-ledger-tool is required to check slots and create snapshots.

```
$ sudo apt-get install svmkit-agave-ledger-tool
```

3. Check the latest optimistic slot on all validators

```
$ sudo -i -u sol agave-ledger-tool -l ledger latest-optimistic-slots
```

Output will look like:

```
                Slot                                         Hash                        Timestamp    Vote Only?
              157666 65DDoDsUFu5tf4N3HuxEhpqMiNeq4qqombE4VjLjdgE8    2025-03-06T12:55:04.579+00:00          true
```

If there are slight differences in the slot numbers between validators (off by 1 or 2), use a slot value that all validators have in common. If the difference is significant, you may need to use a slot from a previous epoch.

4. Generate hard fork snapshot on each validator

Try using the common slot first:

```
$ sudo -i -u sol agave-ledger-tool create-snapshot [COMMON_SLOT] --hard-fork [COMMON_SLOT]
```

If you encounter an error like "The epoch accounts hash cannot be awaited when Invalid!", try using a slot from a previous epoch. For example:

```
$ sudo -i -u sol agave-ledger-tool create-snapshot 157600 --hard-fork 157600
```

Successful output should look like:

```
[2025-03-06T16:13:30.066226548Z INFO  solana_metrics::metrics] datapoint: archive-snapshot-package slot=157600i archive_format="TarZstd" duration_ms=53i full-snapshot-archive-size=393107i
Successfully created snapshot for slot 157600, hash 2kh5hvfnFSHkprX5dgHX8qBggBJjEHb5Y5LKdPnRxvvo: /home/sol/ledger/snapshot-157600-Fh11y82UnfnV3nkGYcJqcuauY8NsCwDmQYr27dNPATkn.tar.zst
Shred version: 34346
```

Note the bank hash value (in the example above, it's `2kh5hvfnFSHkprX5dgHX8qBggBJjEHb5Y5LKdPnRxvvo`) that appears after "Successfully created snapshot for slot".

5. Add hard fork parameters to the validator startup command

Edit the run-validator script on each validator:

```
$ sudo -i -u sol vim run-validator
```

Add the following parameters to the `agave-validator` command:

```
agave-validator \
  --wait-for-supermajority [SLOT] \
  --expected-bank-hash [BANK_HASH] \
  --hard-fork [SLOT] \
  --expected-shred-version [SHRED_VERSION] \
  --no-snapshot-fetch \
  [other existing parameters]
```

Example:
```
agave-validator \
  --wait-for-supermajority 157600 \
  --expected-bank-hash 2kh5hvfnFSHkprX5dgHX8qBggBJjEHb5Y5LKdPnRxvvo \
  --hard-fork 157600 \
  --expected-shred-version 34346 \
  --no-snapshot-fetch \
  [other existing parameters]
```

6. Restart validators in sequence

Start with the bootstrap validator first:

```
$ sudo systemctl restart svmkit-agave-validator.service
```

Wait for the bootstrap validator to stabilize before starting the other validators. This is important because the bootstrap validator only depends on its local ledger while other validators may require connections to working entrypoints.

7. Confirm block production is restored

Check that all validators are now recognized with the correct version:

```
$ solana validators
```

Expected output:
```
Identity                                      Vote Account                            Commission  Last Vote        Root Slot     Skip Rate  Credits  Version            Active Stake
8MgGF4yRhB5SRpyvgsJorgzVYoB5mJqZkVT7Pp8kkQq8  8mQZiAM5MUntnZGib83QUxCh4dybMLkCaErGbH7NXHnZ  100%     157637 (  0)     157606 (  0)   0.00%    32368  1.18.26         9.999999344 SOL (33.33%)
Cmfqr43vcjW7qgRdJhgF6utTZFTjzKPJaucc8SdPoQ8t  HRJUsDx8Mda6tdkfWBqrVPg71jUr3RE4kX9cFbvTRYT7  100%     157637 (  0)     157606 (  0)   0.00%    32368  1.18.26         9.999999344 SOL (33.33%)
FeBH2q4qNmRCzNWVv82xeABERD9cd8u3qmEhmWLtSYQW  4Rz6Kty9qQJ1xYgCuXuQd6xa89rdMb7LzCgwUbcwzSaa  100%     157637 (  0)     157606 (  0)   0.00%    32368  1.18.26         9.999999344 SOL (33.33%)

Stake By Version:
1.18.26 -    3 current validators (100.00%)
```

All validators should show the same version (in this example, 1.18.26). The version displayed will depend on your specific deployment, but the important part is that all validators show a consistent version with no "unknown" entries, and all have active stake.

Once supermajority of active stake agrees on the fork, voting will resume without additional intervention.

## Troubleshooting

- If validators stop with errors after restart, try restarting them in sequence: bootstrap first, then each additional validator.
- It may take some time for all validators to recognize each other and show the correct version information.
- If snapshot creation fails with epoch-related errors, try selecting a slot further back in the previous epoch.