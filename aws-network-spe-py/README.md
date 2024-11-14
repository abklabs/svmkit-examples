# Solana Permissioned Environment Inside an AWS VPC

This example brings up a cluster of Solana validators, all using private addresses, inside an AWS VPC.
Genesis is performed, a snapshot is distributed, and gossip is set up on private addresses inside the VPC.

## Pulumi Configuration Options

| Name              | Description                                                       | Default Value |
| :---------------- | :---------------------------------------------------------------- | :------------ |
| node:count        | The number of nodes to launch, including the bootstrap node.      | 3             |
| node:instanceType | The AWS instance type to use for all of the nodes.                | c6i.xlarge    |
| node:volumeIOPS   | The number of IOPS to provide to the ledger and accounts volumes. | 5000          |

## Running the Example

0. Have `pulumi` installed, logged in to wherever you're storing state, and configured to work with AWS.

- https://www.pulumi.com/docs/iac/cli/commands/pulumi_login/
- https://github.com/pulumi/pulumi-aws?tab=readme-ov-file#configuration

1. Run `pulumi install`; this will install all of the required pieces for this example.

```
% pulumi install
Installing dependencies...

Creating virtual environment...
Finished creating virtual environment
Updating pip, setuptools, and wheel in virtual environment...
Requirement already satisfied: pip in ./venv/lib/python3.13/site-packages (24.2)

.
.
.

Finished installing dependencies
```

2. Create and select a Pulumi stack

```
% pulumi stack init new-spe
Created stack 'new-spe'
```

3. Run `pulumi up`

```
% pulumi up
Please choose a stack, or create a new one: <create a new stack>
Please enter your desired stack name.
To create a stack in an organization, use the format <org-name>/<stack-name> (e.g. `acmecorp/dev`): dev
Created stack 'dev'
Previewing update (dev)

View in Browser (Ctrl+O): https://app.pulumi.com/mylog/dev/previews/390sd21119-5cd0-497d-a945-d86738a9

     Type                       Name                             Plan       Info
 +   pulumi:pulumi:Stack        aws-network-spe-py-dev           create     1 message
 +   ├─ aws:ec2:SecurityGroup   external-access                  create
 +   ├─ aws:ec2:SecurityGroup   internal-access                  create
 +   ├─ tls:index:PrivateKey    bootstrap-node-ssh-key           create
 +   ├─ svmkit:index:KeyPair    bootstrap-node-vote-account-key  create
 +   ├─ svmkit:index:KeyPair    bootstrap-node-validator-key     create
 +   ├─ svmkit:index:KeyPair    stake-account-key                create
 +   ├─ aws:ec2:KeyPair         bootstrap-node-keypair           create
 +   ├─ svmkit:index:KeyPair    faucet-key                       create
 +   ├─ svmkit:index:KeyPair    treasury-key                     create
 +   ├─ svmkit:index:KeyPair    node1-validator-key              create
 +   ├─ aws:ec2:Instance        node1-instance                   create
 +   ├─ svmkit:index:KeyPair    node0-validator-key              create
 +   ├─ svmkit:index:KeyPair    node1-vote-account-key           create
 +   ├─ svmkit:index:KeyPair    node0-vote-account-key           create
 +   ├─ tls:index:PrivateKey    node1-ssh-key                    create
 +   ├─ aws:ec2:KeyPair         node1-keypair                    create
 +   ├─ aws:ec2:Instance        node0-instance                   create
 +   ├─ tls:index:PrivateKey    node0-ssh-key                    create
 +   ├─ aws:ec2:KeyPair         node0-keypair                    create
 +   ├─ aws:ec2:Instance        bootstrap-node-instance          create
 +   ├─ svmkit:genesis:Solana   genesis                          create
 +   ├─ svmkit:validator:Agave  node1-validator                  create
 +   ├─ svmkit:validator:Agave  bootstrap-node-validator         create
 +   └─ svmkit:validator:Agave  node0-validator                  create

Diagnostics:
  pulumi:pulumi:Stack (aws-network-spe-py-dev):
    0 errors, 0 warnings, 0 informations
```

4. Access the bootstrap node to ensure the network is operational and communicating. Initially, only the bootstrap validator will confirm blocks. The other validators are set up to vote and participate in gossip but will not validate blocks until staked.

```
% ./ssh-to-host 0
Warning: Permanently added '54.200.238.38' (ED25519) to the list of known hosts.
Linux ip-172-31-22-205 6.1.0-26-cloud-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.112-1 (2024-09-30) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.

admin@ip-172-31-22-205:~$ solana config set --url http://localhost:8899
Config File: /home/admin/.config/solana/cli/config.yml
RPC URL: http://localhost:8899
WebSocket URL: ws://localhost:8900/ (computed)
Keypair Path: /home/admin/.config/solana/id.json
Commitment: confirmed

admin@ip-172-31-22-205:~$ solana gossip
IP Address      | Identity                                     | Gossip | TPU   | RPC Address           | Version | Feature Set
----------------+----------------------------------------------+--------+-------+-----------------------+---------+----------------
172.31.37.89    | GvwkabqmKSupJ39ZP5tvNo7XGW89neAB9Es9QuLMFMoY | 8001   | 8004  | 172.31.37.89:8899     | 1.18.24 | 3241752014
172.31.44.185   | CZXEQH1QqXuDt6PsXmWppV5nDiYfZRNCJjTk3VQbcvgq | 8001   | 8004  | 172.31.44.185:8899    | 1.18.24 | 3241752014
172.31.40.167   | HJBAoeHmZVywLQv5iXeV5Ph9n8KJPnSx8Qr443R8ta5t | 8001   | 8004  | 172.31.40.167:8899    | 1.18.24 | 3241752014
Nodes: 3

admin@ip-172-31-22-205:~$ solana validators
   Identity                                      Vote Account                            Commission  Last Vote        Root Slot     Skip Rate  Credits  Version            Active Stake
  GvwkabqmKSupJ39ZP5tvNo7XGW89neAB9Es9QuLMFMoY  pABbon2LBNugDkf1t3QBeCA7nbNQPESdXxMw3gqv2fn   100%       1728 (  0)       1697 (  0)   0.00%     1280  1.18.24         0.499999344 SOL (100.00%)

Average Stake-Weighted Skip Rate: 0.00%
Average Unweighted Skip Rate:     0.00%

Active Stake: 0.499999344 SOL

Stake By Version:
1.18.24 -    1 current validators (100.00%)
```

5. Stake the initial validators by running the staking script.

This process involves setting up vote accounts and staking accounts for each validator node. The script will add SSH keys for secure access, create vote accounts, fund validator keys, and delegate stakes to ensure validators are ready to participate in the network. It will also handle any necessary setup and ensure the validator stake is warmed up before confirming the validator state.

```
% ./stake stake-state
```

6. Run token demo script.

This script mints a token and allocates a portion of the supply to a recipient. Initially, the cluster's treasury provides the necessary funds to the minter.

```
% ./token-demo token-demo-state
```

7. (Optional) Tear down the example

```
% pulumi down
```
