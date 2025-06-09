# Frankendancer running on AWS

This example brings up a single Frakendancer validator on AWS.

## Pulumi Configuration Options

| Name                | Description                                               | Default Value |
| :------------------ | :-------------------------------------------------------- | :------------ |
| solana:network      | The known Solana cluster to connect to.                   | testnet       |
| node:instanceType   | The AWS instance type to use for all of the nodes.        | r7a.8xlarge   |
| node:instanceArch   | The AWS architecture type to use for AMI lookup.          | x86_64        |
| node:rootVolumeSize | The size of the AWS instance's root volume, in gigabytes. | 32            |
| node:instanceAmi    | The AMI to use for all of the nodes.                      | _(debian-12)_ |
| node:user           | The user to log into all of the nodes as.                 | admin         |

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

View in Browser (Ctrl+O): https://app.pulumi.com/someaccount/aws-validator-fd-ts/new-validator/previews/3f1f47c9-006a-4d2e-afcc-9f4b8be067d7

     Type                            Name                               Plan
 +   pulumi:pulumi:Stack             aws-validator-fd-ts-new-validator  create
 +   ├─ svmkit:index:KeyPair         validator-key                      create
 +   ├─ tls:index:PrivateKey         ssh-key                            create
 +   ├─ svmkit:index:KeyPair         vote-account-key                   create
 +   ├─ aws:ec2:SecurityGroup        security-group                     create
 +   ├─ svmkit:index:KeyPair         withdrawer-key                     create
 +   ├─ aws:ec2:KeyPair              keypair                            create
 +   ├─ aws:ec2:Instance             instance                           create
 +   └─ svmkit:validator:Firedancer  fd                                 create

Outputs:
    PUBLIC_DNS_NAME: output<string>
    SSH_PRIVATE_KEY: output<string>
    validatorKey   : output<string>
    voteAccountKey : output<string>
    withdrawerKey  : output<string>

Resources:
    + 9 to create

.
.
.

```

4. Verify that the validator has connected to the network.

```
% ./ssh-to-host 0 sudo journalctl -f -u svmkit-fd-validator
INFO:	saving validator host key in /var/folders/56/ljnh2nx524s73bm0dyw3hy780000gn/T/tmp.gsnuaIbzwS/tmp.uxlxVQYehz...
Warning: Permanently added 'ec2-35-86-195-35.us-west-2.compute.amazonaws.com' (ED25519) to the list of known hosts.
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: NOTICE  12-22 13:04:23.220832 2228   14   bank:3 src/disco/topo/fd_topo_run.c(32): booting tile bank:3 pid:2227 tid:2284
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: NOTICE  12-22 13:04:23.256807 2228   15   poh:0 src/disco/topo/fd_topo_run.c(32): booting tile poh:0 pid:2227 tid:2285
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: NOTICE  12-22 13:04:23.284829 2228   17   store:0 src/disco/topo/fd_topo_run.c(32): booting tile store:0 pid:2227 tid:2286
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: NOTICE  12-22 13:04:23.296823 2228   f0   agave src/app/fdctl/run/run_agave.c(208): booting agave pid:2227
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: WARNING 12-22 13:04:23.328786 2228   f0   agave perf/src/lib.rs(51): CUDA is disabled
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: WARNING 12-22 13:04:23.376601 9      f21  0    metrics/src/metrics.rs(324): datapoint: os-config vm.max_map_count=1000000i
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: WARNING 12-22 13:04:23.380596 9      f21  0    metrics/src/metrics.rs(324): datapoint: os-config net.core.optmem_max=20480i
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: WARNING 12-22 13:04:23.382228 9      f21  0    metrics/src/metrics.rs(324): datapoint: os-config net.core.netdev_max_backlog=1000i
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2228]: WARNING 12-22 13:04:23.421123 2228   f0   agave perf/src/perf_libs.rs(107): "/opt/frankendancer/bin/perf-libs" does not exist
Dec 22 13:04:23 ip-172-31-53-101 fdctl[2276]: WARNING 12-22 13:04:23.883328 2276   20   gui:0 src/app/fdctl/run/tiles/fd_gui.c(417): GUI server listening at http://127.0.0.1:80
```

5. Connect to the Frankendancer UI:

```
% ./ssh-to-host 0 -L 8080:localhost:80
```

Now use your local browser to access the proxied HTTP port via [http://localhost:8080](http://localhost:8080).

6. You can then do some of the following by manually:

- Airdrop Solana to your validator's accounts.
- Create a vote account for your validator.
- Create stake for your validator.

Please see the [Solana Operations](https://docs.solanalabs.com/operations/) manual for more information.
To SSH into the validator node you just created, run `./ssh-to-host 0` with no additional arguments.

7. (Optional) Tear down the example

```
% pulumi down
```
