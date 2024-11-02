# Solana Permissioned Environment Inside an AWS VPC

This example brings up a cluster of Solana validators, all using private addresses, inside an AWS VPC.
Genesis is performed, a snapshot is distributed, and gossip is set up on private addresses inside the VPC.

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

2. Run `pulumi up`

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

3. Log into the bootstrap node and verify the network is up and talking.

```
% pulumi stack select dev
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
172.31.22.205   | 6SZhdqo62myLUE4KXWbgzrcGWEcCFhKPVQ2UoM1T6LzR | 8001   | 8004  | 172.31.22.205:8899    | 1.18.24 | 3241752014
172.31.21.22    | FtwBFAtBgpzfvNwP3ErjsuoejavX7pVBkoiymz5P4ksy | 8001   | 8004  | 172.31.21.22:8899     | 1.18.24 | 3241752014
172.31.24.216   | BoKjqpFQvvyDtuRC9bXJnCRLt5rWpGQM9fS3SWUSTzCU | 8001   | none  | none                  | 1.18.24 | 3241752014
Nodes: 3
```

4. Stake the initial validators

```
% ./stake stake-state
```

5. (Optional) Tear down the example

```
% pulumi down
```
