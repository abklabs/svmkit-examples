# Solana Permissioned Environment Inside a GCP VPC using TypeScript

This example brings up a cluster of Solana validators, all using
private addresses, inside a Google Compute VPC.  Genesis is performed,
a snapshot is distributed, and gossip is set up on private addresses
inside the VPC.

## Pulumi Configuration Options

| Name             | Description                                                       | Default Value |
| :----------------| :-----------------------------------------------------------------| :-------------|
| node:count       | The number of nodes to launch, including the bootstrap node.      | 3             |
| node:machineType | The instance type to use for all of the nodes.                    | n1-standard-2 |
| node:osImage     | The operating system image to use for the nodes.                  | debian-12     |
| node:diskSize    | The number of IOPS to provide to the ledger and accounts volumes. | 64 GB         |

NOTE: These configuration settings are not for a production usecase.  They're sized to be allowed in
free-tier GCP accounts, and demonstrate functional behavior.

## Running the Example

0. Have `pulumi` installed, logged in to wherever you're storing state, and configured to work with AWS.

- https://www.pulumi.com/docs/iac/cli/commands/pulumi_login/
- https://www.pulumi.com/registry/packages/gcp/installation-configuration/

1. Run `pulumi install`; this will install all of the required pieces for this example.

```
% pulumi install
Installing dependencies...

yarn install v1.22.22
[1/4] 🔍  Resolving packages...
[2/4] 🚚  Fetching packages...
[3/4] 🔗  Linking dependencies...
[4/4] 🔨  Building fresh packages...
✨  Done in 2.25s.
Finished installing dependencies
```

2. Create and select a Pulumi stack

```
% pulumi stack init new-spe
Created stack 'new-spe'
```

3. Run `pulumi up`

```
Previewing update (new-spe)

View in Browser (Ctrl+O): https://app.pulumi.com/someuser/gcp-network-spe-ts/new-spe/previews/3288dae5-a59d-4458-85a3-1b3716cad12a

     Type                            Name                             Plan
 +   pulumi:pulumi:Stack             gcp-network-spe-ts-new-spe       create
 +   ├─ svmkit:index:KeyPair         node1-vote-account-key           create
 +   ├─ svmkit:index:KeyPair         node0-vote-account-key           create
 +   ├─ svmkit:index:KeyPair         node1-validator-key              create
 +   ├─ svmkit:index:KeyPair         stake-account-key                create
 +   ├─ svmkit:index:KeyPair         treasury-key                     create
 +   ├─ svmkit:index:KeyPair         bootstrap-node-validator-key     create
 +   ├─ tls:index:PrivateKey         node1-ssh-key                    create
 +   ├─ svmkit:index:KeyPair         faucet-key                       create
 +   ├─ svmkit:index:KeyPair         node0-stakeAccount-key           create
 +   ├─ svmkit:index:KeyPair         node0-validator-key              create
 +   ├─ svmkit:index:KeyPair         node1-stakeAccount-key           create
 +   ├─ svmkit:index:KeyPair         bootstrap-node-vote-account-key  create
 +   ├─ tls:index:PrivateKey         bootstrap-node-ssh-key           create
 +   ├─ gcp:compute:Network          network                          create
 +   ├─ tls:index:PrivateKey         node0-ssh-key                    create
 +   ├─ gcp:compute:Subnetwork       subnet                           create
 +   ├─ gcp:compute:Firewall         external                         create
 +   ├─ gcp:compute:Firewall         internal                         create
 +   ├─ gcp:compute:Instance         node0-instance                   create
 +   ├─ gcp:compute:Instance         bootstrap-node-instance          create
 +   ├─ gcp:compute:Instance         node1-instance                   create
 +   ├─ svmkit:genesis:Solana        genesis                          create
 +   ├─ svmkit:validator:Agave       node1-validator                  create
 +   ├─ svmkit:account:Transfer      node0-transfer                   create
 +   ├─ svmkit:validator:Agave       node0-validator                  create
 +   ├─ svmkit:account:Transfer      node1-transfer                   create
 +   ├─ svmkit:account:VoteAccount   node1-voteAccount                create
 +   ├─ svmkit:account:VoteAccount   node0-voteAccount                create
 +   ├─ svmkit:faucet:Faucet         bootstrap-faucet                 create
 +   ├─ svmkit:validator:Agave       bootstrap-node-validator         create
 +   ├─ svmkit:account:StakeAccount  node1-stakeAccount               create
 +   └─ svmkit:account:StakeAccount  node0-stakeAccount               create

.
.
.
```

4. Access the bootstrap node to ensure the network is operational and communicating. Initially, only the bootstrap validator will confirm blocks. The other validators are set up to vote and participate in gossip but will not validate blocks until staked.

```
% ./ssh-to-host 0
Warning: Permanently added '34.121.185.137' (ED25519) to the list of known hosts.
Linux bootstrap-node-instance-5d63d8f 6.1.0-29-cloud-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.123-1 (2025-01-02) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Sat Feb  8 21:13:57 2025 from 122.132.224.111
admin@bootstrap-node-instance-5d63d8f:~$ solana gossip
IP Address      | Identity                                     | Gossip | TPU   | RPC Address           | Version | Feature Set
----------------+----------------------------------------------+--------+-------+-----------------------+---------+----------------
10.0.1.2        | 9ZJ37p2q1JVSwZtmLA9FsWyNdduBDLjTgmcbh6EF8Bf4 | 8001   | 8004  | 10.0.1.2:8899         | 1.18.26 | 3241752014
10.0.1.4        | 7GiDaQ78852T937aFJhz2wTPd6tJL3YvU1MqnAVE6H1y | 8001   | 8004  | 10.0.1.4:8899         | 1.18.26 | 3241752014
10.0.1.3        | DF8myMDobK25b8m2rPeacZYSm9KSdLHoMd89Q6r6Saaz | 8001   | 8004  | 10.0.1.3:8899         | 1.18.26 | 3241752014
Nodes: 3

admin@bootstrap-node-instance-5d63d8f:~$ solana validators
   Identity                                      Vote Account                            Commission  Last Vote        Root Slot     Skip Rate  Credits  Version            Active Stake
  7GiDaQ78852T937aFJhz2wTPd6tJL3YvU1MqnAVE6H1y  FtzUx7aRfNrt1MmsnAnQfg3ztjrbHSRJqGDcf3AaiX1P  100%        222 (-89)        200 (-74)    -           0  1.18.26         0.047024937 SOL (7.92%)
  DF8myMDobK25b8m2rPeacZYSm9KSdLHoMd89Q6r6Saaz  BivdSw5m9rWAUwZtAWPNi76BBRAr31JS7bGqv3qq7yeN  100%        219 (-92)        200 (-74) 100.00%        0  1.18.26         0.047024937 SOL (7.92%)
  9ZJ37p2q1JVSwZtmLA9FsWyNdduBDLjTgmcbh6EF8Bf4  9e4YZEFiUU2b4UVeko2H3L7BQHX8vrSirefFnQ3At2pg  100%        311 (  0)        274 (  0)   0.00%      112  1.18.26         0.499999344 SOL (84.17%)

Average Stake-Weighted Skip Rate: 7.92%
Average Unweighted Skip Rate:     50.00%

Active Stake: 0.594049218 SOL

Stake By Version:
1.18.26 -    3 current validators (100.00%)
```

5. (Optional) Tear down the example

```
% pulumi down
```
