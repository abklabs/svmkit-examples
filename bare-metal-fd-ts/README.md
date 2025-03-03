# Frankendancer running on a remote host

This example brings up a single Frankendancer validator on any remote machine with SSH access.

## Demo Video
[![Watch the video](https://img.youtube.com/vi/dMkJeig4Hh8/0.jpg)](https://www.youtube.com/watch?v=dMkJeig4Hh8)


## Pulumi Configuration Options

| Name              | Description                                                        | Required | Default Value |
| :---------------- | :----------------------------------------------------------------  | :------- | :------------ |
| solana:network    | The known Solana cluster to connect to.                            | no       | testnet       |
| remote:host       | The hostname of the remote machine.                                | yes      |               |
| remote:user       | The login user of the remote machine.                              | yes      |               |
| remote:privateKey | **(SECRET)** The OpenSSH (PEM) private key for the remote machine. | yes      |               |

## Running the Example

0. Have `pulumi` installed, logged in to wherever you're storing state, and configured to work with AWS.

- https://www.pulumi.com/docs/iac/cli/commands/pulumi_login/
- https://github.com/pulumi/pulumi-aws?tab=readme-ov-file#configuration

1. If the remote machine has inbound network traffic blocked by default, ensure that inbound traffic is allowed on TCP ports 8000-8020 and UDP ports 8000-8020 and 8900-8920.

2. Run `pulumi install`; this will install all of the required pieces for this example.

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

3. Create and select a Pulumi stack

```
% pulumi stack init new-validator
Created stack 'new-validator'
```

4. Provide the credentials for connecting to the machine via SSH with `pulumi config`

```
% pulumi config set remote:host my-host.example
% pulumi config set remote:user my-user
% pulumi config set --secret remote:privateKey < my-access-key.pem
```

5. Run `pulumi up`

```
% pulumi up
Previewing update (testing)

View in Browser (Ctrl+O): https://app.pulumi.com/someaccount/bare-metal-fd-ts/new-validator/previews/3f1f47c9-006a-4d2e-afcc-9f4b8be067d7

     Type                            Name                               Plan       
 +   pulumi:pulumi:Stack             bare-metal-agave-ts-new-validator  create     
 +   ├─ svmkit:index:KeyPair         validator-key                      create     
 +   ├─ svmkit:index:KeyPair         vote-account-key                   create     
 +   ├─ svmkit:index:KeyPair         withdrawer-key                     create     
 +   └─ svmkit:validator:Firedancer  fd                                 create     

Outputs:
    nodes_name       : [
        [0]: "instance"
    ]
    nodes_private_key: [
        [0]: [secret]
    ]
    nodes_public_ip  : [
        [0]: "my-host.example"
    ]
    nodes_user       : [
        [0]: "my-user"
    ]
    validatorKey     : output<string>
    voteAccountKey   : output<string>
    withdrawerKey    : output<string>

Resources:
    + 5 to create
```

6. Verify that the validator has connected to the network.

```
% ./ssh-to-host 0 sudo journalctl -f -u svmkit-fd-validator
Warning: Permanently added 'my-host.example' (ED25519) to the list of known hosts.
Feb 14 23:17:46 host652096 systemd[1]: Starting svmkit-fd-validator.service - SVMkit FD Validator...
Feb 14 23:17:46 host652096 systemd[1]: Started svmkit-fd-validator.service - SVMkit FD Validator.
Feb 14 23:17:47 host652096 fdctl[839211]: Log at "/tmp/fd-0.0.0_839211_sol_host652096_2025_02_14_23_17_47_291751494_GMT+00"
Feb 14 23:17:47 host652096 fdctl[839211]: NOTICE  02-14 23:17:47.295840 839211 f0   main src/disco/topo/fd_topo.c(446):
Feb 14 23:17:47 host652096 fdctl[839211]: SUMMARY
Feb 14 23:17:47 host652096 fdctl[839211]:               Total Tiles: 23
Feb 14 23:17:47 host652096 fdctl[839211]:       Total Memory Locked: 57220812800 bytes (53 GiB + 298 MiB + 20 KiB)
Feb 14 23:17:47 host652096 fdctl[839211]:   Required Gigantic Pages: 53
Feb 14 23:17:47 host652096 fdctl[839211]:       Required Huge Pages: 149
Feb 14 23:17:47 host652096 fdctl[839211]:     Required Normal Pages: 43
Feb 14 23:17:47 host652096 fdctl[839211]:   Required Gigantic Pages (NUMA node 0): 53
Feb 14 23:17:47 host652096 fdctl[839211]:       Required Huge Pages (NUMA node 0): 149
Feb 14 23:17:47 host652096 fdctl[839211]:            Agave Affinity: 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47
```

7. Connect to the Frankendancer UI:

```
% ./ssh-to-host 0 -L 8080:localhost:80
```

Now use your local browser to access the proxied HTTP port via [http://localhost:8080](http://localhost:8080).

8. You can then do some of the following manually:

- Airdrop Solana to your validator's accounts.
- Create a vote account for your validator.
- Create stake for your validator.

Please see the [Solana Operations](https://docs.solanalabs.com/operations/) manual for more information.
To SSH into the validator node you just spun up, run `./ssh-to-host 0` with no additional arguments.

9. (Optional) Tear down the example

```
% pulumi down
```
