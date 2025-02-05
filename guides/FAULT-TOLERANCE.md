# Cluster Fault Tolerance Guide for SVM Networks

## Introduction

This guide explains how stake distribution impacts fault tolerance, and how to calculate the maximum allowable node failures while maintaining consensus in an SVM network.

## Consensus and Supermajority

### What is Consensus?

Consensus is the minimum percentage of total stake required for a network to continue producing blocks. In Solana-based networks, consensus is 66.67% (2/3) of total stake. If stake controlled by active validators falls below 66.67%, consensus is lost, and the network halts.

### What is Supermajority?

A supermajority is required to agree on the slot for a hard-fork networks. The supermajority is defined as 80% and is configured as a constant within the validator binary.

### Calculating Maximum Node Failures

To maintain consensus, the remaining stake must be at least 66.67% of the total stake.

#### Example: 5-Node Cluster

- Stake is evenly distributed (each validator holds 20% of total stake).
- Consensus requires 4 nodes.
- 1 node can go down safely, but if 2 nodes fail, the network halts.

#### Example: 7-Node Cluster

- Each validator has 1/7th (≈14.29%) of the stake.
- To maintain 66.67%, at least 5 nodes must remain online.
- Up to 2 nodes can fail without halting the network.

## Reference Table

| Total Nodes | Minimum Nodes Required | Max Node Failures Allowed | Active Stake (%) |
| ----------- | ---------------------- | ------------------------- | ---------------- |
| 3           | 3                      | 0                         | 100              |
| 4           | 3                      | 1                         | 75               |
| 5           | 4                      | 1                         | 80               |
| 6           | 4                      | 2                         | 66.67            |
| 7           | 5                      | 2                         | 71.43            |
| 8           | 6                      | 2                         | 75               |
| 9           | 6                      | 3                         | 66.67            |
| 10          | 7                      | 3                         | 70               |

## Best Practices for Fault Tolerance

1. **Minimum of 4 Validators:**
   - Avoid 3-node clusters as any single failure halts the network.
   - Running 5+ validators improves resilience.
2. **Distribute Stake Evenly:**
   - Uneven stake can create single points of failure.
3. **Monitor Validator Health:**
   - Use solana validators to check for delinquent nodes.
   - Example of a delinquent node:
     ```
     ⚠️  ValidatorX  VoteAccountXYZ  100%       3245             3214       100.00%        0  unknown         9.999999344 SOL (20.00%)
     ```

## Conclusion

- Consensus requires 66.67% of the total stake.
- A supermajority, set at 80% of the stake, is necessary for the network to approve a hard-fork.
- A 3-node cluster is vulnerable to a single node failure.
- Recommended practice: Operate with a minimum of 4 validators and ensure even stake distribution.
