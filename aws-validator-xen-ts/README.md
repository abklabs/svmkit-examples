# X1 Validator running on AWS

This example deploys a single X1 testnet validator on AWS. It is a non-voting, functional demonstration and is not intended for production use. For the additional instructions needed to setup a voting validator, please refer to the official [X1 documentation](https://docs.x1.xyz/validating/create-a-validator-node).

## Demo Video

[![YouTube Video](https://img.youtube.com/vi/QMZE24w71uE/0.jpg)](https://www.youtube.com/watch?v=QMZE24w71uE)


## Pulumi Configuration Options

| Name                | Description                                                       | Default Value |
|:--------------------|:------------------------------------------------------------------|:--------------|
| node:instanceType   | The AWS instance type to use for all of the nodes.                | t3.2xlarge    |
| node:instanceArch   | The AWS architecture type to use for AMI lookup.                  | x86\_64       |
| node:volumeIOPS     | The number of IOPS to provide to the ledger and accounts volumes. | 5000          |
| node:rootVolumeSize | The size of the AWS instance's root volume, in gigabytes.         | 32            |
| node:instanceAmi    | The AMI to use for all of the nodes.                              | _(debian-12)_ |
| node:user           | The user to log into all of the nodes as.                         | admin         |

### Performance testing

 The default configuration for IOPS is targeted at functional testing.
 For perfomance testing, set node:volumeIOPS to 16000.

## Running the Example

0. Have `pulumi` installed, logged in to wherever you're storing state, and configured to work with AWS.

- https://www.pulumi.com/docs/iac/cli/commands/pulumi_login/
- https://github.com/pulumi/pulumi-aws?tab=readme-ov-file#configuration

1. Run `pulumi install`; this will install all of the required pieces for this example.

```
% pulumi install
Installing dependencies...

yarn install v1.22.22
[1/4] 🔍  Resolving packages...
[2/4] 🚚  Fetching packages...
[3/4] 🔗  Linking dependencies...
[4/4] 🔨  Building fresh packages...
✨  Done in 3.69s.
Finished installing dependencies
```

2. Create and select a Pulumi stack

```
% pulumi stack init new-validator
Created stack 'new-validator'
```

3. Run `pulumi up`

```
% pulumi up
Previewing update (new-validator)

.
.
.

Do you want to perform this update? yes
Updating (new-validator)

     Type                       Name                            Status
 +   pulumi:pulumi:Stack        aws-validator-agave-ts-new-validator  created (60s)
 +   ├─ svmkit:index:KeyPair    vote-account-key                      created (0.18s)
 +   ├─ svmkit:index:KeyPair    validator-key                         created (0.39s)
 +   ├─ tls:index:PrivateKey    ssh-key                               created (0.29s)
 +   ├─ aws:ec2:SecurityGroup   security-group                        created (4s)
 +   ├─ aws:ec2:KeyPair         keypair                               created (0.70s)
 +   ├─ aws:ec2:Instance        instance                              created (14s)
 +   └─ svmkit:validator:Agave  validator                             created (36s)

Outputs:
    PUBLIC_DNS_NAME: "ec2-35-86-146-3.us-west-2.compute.amazonaws.com"
    SSH_PRIVATE_KEY: [secret]

Resources:
    + 8 created

Duration: 1m2s
```

4. Verify that the validator has connected to the network.

```
% ./ssh-to-host 0 journalctl -f -u svmkit-tachyon-validator
[2024-11-20T17:50:24.275774661Z INFO  solana_download_utils] downloaded 3048373992 bytes 9.3% 17468680.0 bytes/s
[2024-11-20T17:50:30.278042126Z INFO  solana_download_utils] downloaded 3154173560 bytes 9.6% 17626600.0 bytes/s
[2024-11-20T17:50:36.286639128Z INFO  solana_download_utils] downloaded 3259296912 bytes 10.0% 17495494.0 bytes/s
[2024-11-20T17:50:42.291898545Z INFO  solana_download_utils] downloaded 3364530312 bytes 10.3% 17523540.0 bytes/s
[2024-11-20T17:50:48.297096944Z INFO  solana_download_utils] downloaded 3470044624 bytes 10.6% 17570496.0 bytes/s
```

5. You can then do some of the following by manually:

- Airdrop Solana to your validator's accounts.
- Create a vote account for your validator.
- Create stake for your validator.

To SSH into the validator node you just created, run `./ssh-to-host 0` with no additional arguments.

6. (Optional) Tear down the example

```
% pulumi down
```
