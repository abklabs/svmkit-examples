# Solana Validator running on GCP

This example brings up a single Solana validator on GCP.  This is a
non-voting functional example, and shouldn't used for any production
use case.  You may have performance problems with the default
`node:instanceType`.

[![Watch the video](https://img.youtube.com/vi/jHvUuGpmU9o/0.jpg)](https://youtu.be/jHvUuGpmU9o)

## Pulumi Configuration Options

| Name              | Description                                                               | Required | Default Value |
| :---------------- | :------------------------------------------------------------------------ | :------- | :------------ |
| solana:network    | The known Solana cluster to connect to.                                   | no       | testnet       |
| validator:version | The version of the validator APT package to install.                      | no       | 2.2.14-1      |
| node:instanceType | The GCP instance type to use for all of the nodes.                        | no       | c4-standard-8 |
| node:diskSize     | The size of the volume to use for OS, accounts, and ledger, in gigabytes. | no       | 256           |
| gcp:project       | The GCP project to create all resources under.                            | no       | _(system)_    |
| gcp:region        | The GCP region to create all resources in.                                | yes      |               |
| gcp:zone          | The **fully-qualified** GCP availability zone to create all resources in. | yes      |               |
| node:user         | The user to log into all of the nodes as.                                 | no       | admin         |

## Running the Example

0. Have `pulumi` installed, logged in to wherever you're storing state, and configured to work with GCP.

- https://www.pulumi.com/docs/iac/cli/commands/pulumi_login/
- https://github.com/pulumi/pulumi-gcp?tab=readme-ov-file#google-cloud-platform-resource-provider

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

View in Browser (Ctrl+O): https://app.pulumi.com/someuser/gcp-validator-agave-ts/new-validator/updates/1

     Type                       Name                             Status
 +   pulumi:pulumi:Stack        gcp-validator-agave-ts-asg-test  created (124s)
 +   ├─ svmkit:index:KeyPair    validator-key                    created (0.12s)
 +   ├─ gcp:compute:Network     network                          created (21s)
 +   ├─ svmkit:index:KeyPair    vote-account-key                 created (0.20s)
 +   ├─ tls:index:PrivateKey    ssh-key                          created (0.10s)
 +   ├─ gcp:compute:Subnetwork  subnet                           created (22s)
 +   ├─ gcp:compute:Firewall    firewall                         created (11s)
 +   ├─ gcp:compute:Instance    instance                         created (40s)
 +   └─ svmkit:validator:Agave  validator                        created (36s)

Outputs:
    nodes: [
        ...
    ]

Resources:
    + 9 created

Duration: 2m6s
```

4. Verify that the validator has connected to the network.

```
% ./ssh-to-host 0 journalctl -f -u svmkit-agave-validator
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

Please see the [Solana Operations](https://docs.solanalabs.com/operations/) manual for more information.
To SSH into the validator node you just created, run `./ssh-to-host 0` with no other arguments.

6. (Optional) Tear down the example

```
% pulumi down
```
