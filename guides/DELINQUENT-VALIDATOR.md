# Delinquent Validator

## What Does It Mean for a Validator to Be Delinquent?

A delinquent validator is one that has stopped voting or producing blocks and is no longer actively participating in consensus. The validator will be marked as “Delinquent” in the output of solana validators if it fails to vote for a prolonged period (typically after 128 missed slots, or about 12.8 seconds on mainnet-beta).

Common Reasons for Delinquency:

• Network connectivity issues
• Hardware or resource exhaustion (CPU, memory, disk I/O)
• Software crashes or misconfigurations
• Outdated Solana software version
• Running with an insufficient stake and getting skipped

Example Output of a Delinquent Validator:

```
solana validators

   Identity                                      Vote Account                            Commission  Last Vote        Root Slot     Skip Rate  Credits  Version            Active Stake
  2B79QyF9idx6fnDbsQto5kxmiphFaZihGQRhLHs1ULp1  7V4beuNHASzj7LXSz7bGaAoQXSjeb38QS9itFPy1LyJe  100%       4108 (  0)       4059 (  0)   0.00%        0  1.18.26         9.999999344 SOL (25.00%)
  HA6bFQhwq9D4Ky4ktQYXbJBWVTPd3waCF9aq5a4gscPG  6BwD54hsoopcELhKn6wmPv4MUzh8MiLiuT5bTCqVvvVQ  100%       4108 (  0)       4059 (  0)   0.00%        0  1.18.26         9.999999344 SOL (25.00%)
  BKi2EPLT2nZcPimmZ8uUsyx6tquioeuYnRR8Bhoi4dKq  8zVEyvu2Bj4iAUqy6XMW8RhdU3K5gsP5hKVxBJQxFEgW  100%       4108 (  0)       4059 (  0)   0.00%        0  1.18.26         9.999999344 SOL (25.00%)
⚠️  31cNaRo15yoLaJ6sifaikdTbKpFJ4HQ6GQmD8Nu3yUyZ  6A4LNBdhtZdMdTaWhTVu7jKcuy5QPfoeDYfg2vnNvMCg  100%       3827             3796       100.00%        0  unknown         9.999999344 SOL (25.00%)

Average Stake-Weighted Skip Rate: 25.00%
Average Unweighted Skip Rate:     25.00%

Active Stake: 39.999997376 SOL
Current Stake: 29.999998032 SOL (75.00%)
Delinquent Stake: 9.999999344 SOL (25.00%)

Stake By Version:
1.18.26 -    3 current validators (75.00%)
unknown -    0 current validators ( 0.00%)   1 delinquent validators (25.00%)
```

## Recovery Steps

> **Note:** This guide is based on the Agave validator. System unit names may differ depending on the SVMKIT validator variant.

1. Check Validator Logs

Run the following command to check recent logs:

```
journalctl -n 100 -u svmkit-agave-validator
```

Look for errors related to connection issues, missing votes, or performance degradation.

2. Check System Resource Usage

Verify system performance using htop or top:

```
sudo apt install htop -y
htop
```

Check disk usage and IOPS:

```
sudo apt install sysstat -y
iostat -xm 5
```

If CPU is pegged at 100% or RAM usage is excessive, consider optimizing hardware or reducing load.

3. Ensure the Validator is Running

Check if the validator process is active:

```
systemctl status svmkit-agave-validator
```

If it’s not running, restart it:

```
systemctl restart svmkit-agave-validator
```

4. Use Catchup to Track the Validator

Monitor how far behind the validator is:

```
solana catchup --our-localhost
⠐ 871 slot(s) behind (us:3798 them:4669), our node is falling behind at -2.2 slots/second (AVG: -2.8 slots/second)
```

If the validator is struggling to catch up, check logs for issues related to voting on the heaviest fork or interpreting the leader schedule:

```
journalctl -u svmkit-agave-validator
```

Example of failure logs:

```
[2025-02-24T08:52:27.534731204Z INFO solana_core::replay_stage] Couldn't vote on heaviest fork: 3863, heaviest_fork_failures: [FailedThreshold(3863, 4, 9999999344, 39999997376)]
[2025-02-24T08:52:27.534765676Z ERROR solana_core::replay_stage] 31cNaRo15yoLaJ6sifaikdTbKpFJ4HQ6GQmD8Nu3yUyZ No next leader found
```

If the validator is unable to vote or follow the heaviest fork, a reboot from a fresh snapshot is required.

5. Reset the Validator Ledger

The simplest way to restart a validator is to delete the ledger directory and let the validator download a fresh snapshot from an entrypoint.

Steps to Reset the Validator:

```
# Stop the validator

sudo systemctl stop svmkit-agave-validator

# Clear the ledger directory

sudo rm -rf /home/sol/ledger/*

# Restart the validator

sudo systemctl restart svmkit-agave-validator
```

6. Monitor Validator Recovery

After restarting, ensure your validator is catching up:

```
solana catchup --our-localhost
31cNaRo15yoLaJ6sifaikdTbKpFJ4HQ6GQmD8Nu3yUyZ has caught up (us:6676 them:6676)
```

Once caught up, confirm the validator is voting again:

```
solana validators
   Identity                                      Vote Account                            Commission  Last Vote        Root Slot     Skip Rate  Credits  Version            Active Stake
  BKi2EPLT2nZcPimmZ8uUsyx6tquioeuYnRR8Bhoi4dKq  8zVEyvu2Bj4iAUqy6XMW8RhdU3K5gsP5hKVxBJQxFEgW  100%       9608 (  0)       9577 (  0)   0.00%     1376  1.18.26         9.999999344 SOL (25.00%)
  2B79QyF9idx6fnDbsQto5kxmiphFaZihGQRhLHs1ULp1  7V4beuNHASzj7LXSz7bGaAoQXSjeb38QS9itFPy1LyJe  100%       9608 (  0)       9577 (  0)   0.00%     1376  1.18.26         9.999999344 SOL (25.00%)
  HA6bFQhwq9D4Ky4ktQYXbJBWVTPd3waCF9aq5a4gscPG  6BwD54hsoopcELhKn6wmPv4MUzh8MiLiuT5bTCqVvvVQ  100%       9608 (  0)       9577 (  0)   0.00%     1376  1.18.26         9.999999344 SOL (25.00%)
  31cNaRo15yoLaJ6sifaikdTbKpFJ4HQ6GQmD8Nu3yUyZ  6A4LNBdhtZdMdTaWhTVu7jKcuy5QPfoeDYfg2vnNvMCg  100%       9608 (  0)       9577 (  0)   0.00%     1376  1.18.26         9.999999344 SOL (25.00%)

Average Stake-Weighted Skip Rate: 0.00%
Average Unweighted Skip Rate:     0.00%

Active Stake: 39.999997376 SOL

Stake By Version:
1.18.26 -    4 current validators (100.00%)
```
