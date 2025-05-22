# Solana Permissioned Environment Inside an AWS VPC

This example brings up a cluster of Solana validators, all using private addresses, inside an AWS VPC.
Genesis is performed, a snapshot is distributed, and gossip is set up on private addresses inside the VPC.

![An example of launching an SPE on AWS](https://github.com/abklabs/svmkit-media/blob/main/SVMKitSPELaunch/10x_speed_shorter.gif?raw=true)

## Here's a short explainer video:

[![YouTube Video](https://img.youtube.com/vi/8rgUikRios4/0.jpg)](https://www.youtube.com/embed/8rgUikRios4?si=lqUuZfgD_9fImpG0)

## Performance Benchmarks

The default configuration of this Solana validator cluster can achieve the following transaction processing performance:

```
[2025-04-04T18:42:43.913253413Z INFO  solana_bench_tps::bench]  Node address        |       Max TPS | Total Transactions
[2025-04-04T18:42:43.913256071Z INFO  solana_bench_tps::bench] ---------------------+---------------+--------------------
[2025-04-04T18:42:43.913258431Z INFO  solana_bench_tps::bench] http://localhost:8899 |       7006.67 | 210480 
    Average max TPS: 7006.67, 0 nodes had 0 TPS
    Highest TPS: 7006.67 sampling period 1s max transactions: 210480 clients: 1 drop rate: 0.00
[2025-04-04T18:42:43.913305787Z INFO  solana_bench_tps::bench] 	Average TPS: 3406.448
```

This benchmark was conducted using the following command:

```bash
solana-bench-tps \
  --client-node-id /home/sol/validator-keypair.json \
  --use-tpu-client \
  --tx-count 3500 \
  --duration 60 \
  --url "http://localhost:8899" \
  --num-lamports-per-account 10000
```

System utilization during benchmark:
- CPU Utilization: Average 56.19%
- Memory Utilization: ~4.3GB
- Network Traffic: ~1100Kbps inbound, ~2500Kbps outbound

## Pulumi Configuration Options

| Name              | Description                                                       | Default Value |
| :---------------- | :---------------------------------------------------------------- | :------------ |
| node:count        | The number of nodes to launch, including the bootstrap node.      | 3             |
| node:instanceType | The AWS instance type to use for all of the nodes.                | c6i.xlarge    |
| node:instanceArch | The AWS instance architecture type to use for the AMI lookup.     | x86_64        |
| node:volumeIOPS   | The number of IOPS to provide to the ledger and accounts volumes. | 5000          |
| network:vpcId     | The AWS VPC id to deploy the example into.                        | Default VPC   |
| validator:version | The version of the validator APT package to install.              | 2.2.14-1      |

Note: All EC2 instances must have a public IPv4 addresses.  This is a limitation of the example,
not of AWS or svmkit.

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
% ./ssh-to-host 0 solana gossip
Warning: Permanently added '34.221.138.152' (ED25519) to the list of known hosts.
IP Address      | Identity                                     | Gossip | TPU   | RPC Address           | Version | Feature Set
----------------+----------------------------------------------+--------+-------+-----------------------+---------+----------------
172.31.15.168   | FaWcX8EgsvNVzneG9AWxPbc4tW7TwdGHoiLttS4vCJZX | 8001   | 8004  | 172.31.15.168:8899    | 1.18.24 | 3241752014
172.31.15.107   | DhCUqnynb172CV4SZBaSUBpC156SAMoeo6kBvcwNFbz7 | 8001   | 8004  | 172.31.15.107:8899    | 1.18.24 | 3241752014
172.31.7.92     | ENzVE5FCbgjQhrmRCtRowaWk16qjvJFScinpHf12rg9d | 8001   | 8004  | 172.31.7.92:8899      | 1.18.24 | 3241752014
Nodes: 3

% ./ssh-to-host 0 solana validators
Warning: Permanently added '34.221.138.152' (ED25519) to the list of known hosts.
   Identity                                      Vote Account                            Commission  Last Vote        Root Slot     Skip Rate  Credits  Version            Active Stake
  FaWcX8EgsvNVzneG9AWxPbc4tW7TwdGHoiLttS4vCJZX  FwHm1TwydnqnGskixP8Dhi3TWDhoJQYp6tPm2YFykjUi  100%        292 (  0)        261 (  0)   0.00%        0  1.18.24         0.499999344 SOL (100.00%)

Average Stake-Weighted Skip Rate: 0.00%
Average Unweighted Skip Rate:     0.00%

Active Stake: 0.499999344 SOL

Stake By Version:
1.18.24 -    1 current validators (100.00%)
```

5. Run token demo script.

This script mints a token and allocates a portion of the supply to a recipient. Initially, the cluster's treasury provides the necessary funds to the minter.

```
% ./token-demo token-demo-state
```

6. Access the RPC and Explorer via Port Forwarding (Optional)

In the example, the deployed validators and explorer are running remotely, so you’ll need to forward the relevant ports to your local machine if you wish to interact with the RPC API or view the Explorer in your browser. The Solana JSON RPC API typically listens on port 8899 and the Explorer on port 3000.


Forward the ports to your local machine:

```
./ssh-to-host 0 -L 8899:localhost:8899 -L 3000:localhost:3000
```
Test the RPC API by running the following command:
```
curl http://localhost:8899 -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0","id": 1,"method": "getHealth"}'
```
Additionally you can set your local Solana config to the same port to interact with the cluster:
```
solana set --url http://localhost:8899

solana block
```
View the explorer for the SPE in your browser at `http://localhost:3000` . Note that the explorer
frontend requires access to the node as well, so you need to make sure you've forwarded the
validator's RPC port to your local machine as well.


7. (Optional) Tear down the example

```
% pulumi down
```
