import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
import pulumi_svmkit as svmkit
from typing import cast, List

from spe import Node, Agave, AGAVE_VERSION, ValidatorLayout, Firedancer, GOSSIP_PORT, RPC_PORT, FAUCET_PORT


node_config = pulumi.Config("node")

total_nodes = node_config.get_int("count") or 3
node_layout = node_config.get_object("layout") or None

node_manifest: List[ValidatorLayout] = (
    [{"kind": layout.get("kind"), "version": layout.get("version")}
     for layout in node_layout]
    if node_layout
    else [{"kind": "agave", "version": AGAVE_VERSION}] * total_nodes
)

tuner_config = pulumi.Config("tuner")

# Watchtower Notification Config
watchtower_config = pulumi.Config("watchtower")

slack_webhook_url = watchtower_config.get("slack_webhook_url") or None
discord_webhook_url = watchtower_config.get("discord_webhook_url") or None
telegram_bot_token = watchtower_config.get("telegram_bot_token") or None
telegram_chat_id = watchtower_config.get("telegram_chat_id") or None
pagerduty_integration_key = watchtower_config.get(
    "pagerduty_integration_key") or None
twilio_account_sid = watchtower_config.get("twilio_account_sid") or None
twilio_auth_token = watchtower_config.get("twilio_auth_token") or None
twilio_to_number = watchtower_config.get("twilio_to_number") or None
twilio_from_number = watchtower_config.get("twilio_from_number") or None

bootstrap_node = Node("bootstrap-node")
faucet_key = svmkit.KeyPair("faucet-key")
treasury_key = svmkit.KeyPair("treasury-key")
stake_account_key = svmkit.KeyPair("stake-account-key")

genesis = svmkit.genesis.Solana(
    "genesis",
    connection=bootstrap_node.connection,
    version=AGAVE_VERSION,
    flags={
        "ledger_path": "/home/sol/ledger",
        "identity_pubkey": bootstrap_node.validator_key.public_key,
        "vote_pubkey": bootstrap_node.vote_account_key.public_key,
        "stake_pubkey": stake_account_key.public_key,
        "faucet_pubkey": faucet_key.public_key,
        "enable_warmup_epochs": True,
        "bootstrap_validator_stake_lamports": 10000000000,  # 10 SOL
    },
    primordial=[
        {
            "pubkey": bootstrap_node.validator_key.public_key,
            "lamports": "1000000000000",  # 1000 SOL
        },
        {
            "pubkey": treasury_key.public_key,
            "lamports": "100000000000000",  # 100000 SOL
        },
        {
            "pubkey": faucet_key.public_key,
            "lamports": "1000000000000",  # 1000 SOL
        },
    ],
    opts=pulumi.ResourceOptions(
        depends_on=[bootstrap_node.instance])
)

sol_env = svmkit.solana.EnvironmentArgs(
    rpc_url=bootstrap_node.instance.private_ip.apply(
        lambda ip: f"http://{ip}:{RPC_PORT}")
)

rpc_faucet_address = bootstrap_node.instance.private_ip.apply(
    lambda ip: f"{ip}:{FAUCET_PORT}"
)

faucet = svmkit.faucet.Faucet(
    "bootstrap-faucet",
    connection=bootstrap_node.connection,
    keypair=faucet_key.json,
    flags={
        "per_request_cap": 1000,
    },
    opts=pulumi.ResourceOptions(depends_on=[genesis]))

bootstrap_manifest = node_manifest[0]
bootstrap_kind = bootstrap_manifest.get("kind")
bootstrap_version = bootstrap_manifest.get("version")

if bootstrap_kind == "agave":
    bootstrap_validator = Agave(
        "bootstrap",
        node=bootstrap_node,
        version=bootstrap_version,
        flags=svmkit.agave.FlagsArgsDict({
            "allow_private_addr": True,
            "block_production_method": "central-scheduler",
            "dynamic_port_range": "8002-8020",
            "enable_extended_tx_metadata_storage": True,
            "enable_rpc_transaction_history": True,
            "full_rpc_api": True,
            "full_snapshot_interval_slots": 1000,
            "gossip_host": bootstrap_node.instance.private_ip,
            "gossip_port": GOSSIP_PORT,
            "no_voting": False,
            "no_wait_for_vote_to_start_leader": True,
            "rpc_bind_address": "0.0.0.0",
            "rpc_faucet_address": rpc_faucet_address,
            "rpc_port": RPC_PORT,
            "use_snapshot_archives_at_startup": "when-newest",
            "wal_recovery_mode": "skip_any_corrupted_record",
        }),
        environment=sol_env,
        startup_policy={
            "wait_for_rpc_health": True
        },
        opts=pulumi.ResourceOptions(depends_on=[faucet])
    )
elif bootstrap_kind == "firedancer":
    bootstrap_validator = Firedancer(
        "bootstrap",
        node=bootstrap_node,
        version=bootstrap_version,
        config=svmkit.firedancer.ConfigArgsDict({
            "user": "sol",
            "gossip": svmkit.firedancer.ConfigGossipArgsDict({
                "host": bootstrap_node.instance.private_ip,
                "entrypoints": [bootstrap_node.instance.private_ip.apply(
                    lambda ip: f"{ip}:{GOSSIP_PORT}")]
            }),
            "consensus": svmkit.firedancer.ConfigConsensusArgsDict({
                "known_validators": [bootstrap_node.validator_key.public_key],
                "expected_genesis_hash": genesis.genesis_hash,
                "identity_path": "/home/sol/validator-keypair.json",
                "vote_account_path": "/home/sol/vote-account-keypair.json",
                "wait_for_vote_to_start_leader": False,
            }),
            "layout": svmkit.firedancer.ConfigLayoutArgsDict({
                "affinity": "auto",
                "agave_affinity": "auto",
                "bank_tile_count": 2,
                "verify_tile_count": 1,
            }),
            "ledger": svmkit.firedancer.ConfigLedgerArgsDict({
                "path": "/home/sol/ledger",
                "accounts_path": "/home/sol/accounts",
            }),
            "rpc": svmkit.firedancer.ConfigRPCArgsDict({
                "port": RPC_PORT,
                "full_api": True,
                "private": False,
                "transaction_history": True,
                "extended_tx_metadata_storage": True,
                "only_known": False,
                "pubsub_enable_block_subscription": False,
                "pubsub_enable_vote_subscription": False,
                "bigtable_ledger_storage": False,
            }),
            "extra_config": [
                """
[development]
  [development.gossip]
     allow_private_address = true
"""
            ]
        }),
        environment=sol_env,
        opts=pulumi.ResourceOptions(depends_on=[faucet])
    )
else:
    raise ValueError("Unknown validator kind")


explorer = svmkit.explorer.Explorer(
    "bootstrap-explorer",
    connection=bootstrap_node.connection,
    environment=sol_env,
    name="Demo",
    symbol="DMO",
    cluster_name="demonet",
    rpcurl="http://localhost:8899",
    flags={
        "hostname": "0.0.0.0",
        "port": 3000,
    },
    opts=pulumi.ResourceOptions(depends_on=[bootstrap_validator]))

consensus_manifest = node_manifest[1:]

nodes = [Node(f"node{n}") for n in range(len(consensus_manifest))]
all_nodes = [bootstrap_node] + nodes

for i, node in enumerate(nodes):
    other_nodes = [x for x in all_nodes if x != node]

    entry_point = [x.instance.private_ip.apply(
        lambda v: f"{v}:{GOSSIP_PORT}") for x in other_nodes]
    known_validators = [x.validator_key.public_key for x in other_nodes]
    expected_genesis_hash = genesis.genesis_hash

    validator_kind = consensus_manifest[i]["kind"]
    validator_version = consensus_manifest[i]["version"]

    if validator_kind == "agave":
        validator = Agave(node.name,
                          node=node,
                          version=validator_version,
                          flags=svmkit.agave.FlagsArgsDict({
                              "allow_private_addr": True,
                              "block_production_method": "central-scheduler",
                              "dynamic_port_range": "8002-8020",
                              "entry_point": entry_point,
                              "expected_genesis_hash": expected_genesis_hash,
                              "full_rpc_api": False,
                              "full_snapshot_interval_slots": 1000,
                              "gossip_host": node.instance.private_ip,
                              "gossip_port": GOSSIP_PORT,
                              "known_validator": known_validators,
                              "limit_ledger_size": 50000000,
                              "no_voting": False,
                              "no_wait_for_vote_to_start_leader": True,
                              "only_known_rpc": False,
                              "private_rpc": False,
                              "rpc_bind_address": "0.0.0.0",
                              "rpc_faucet_address": rpc_faucet_address,
                              "rpc_port": RPC_PORT,
                              "use_snapshot_archives_at_startup": "when-newest",
                              "wal_recovery_mode": "skip_any_corrupted_record",
                          }),
                          environment=sol_env,
                          startup_policy=svmkit.agave.StartupPolicyArgs(),
                          opts=pulumi.ResourceOptions(depends_on=[node.instance, bootstrap_validator]))
    elif validator_kind == "firedancer":
        validator = Firedancer(
            node.name,
            node=node,
            version=validator_version,
            config=svmkit.firedancer.ConfigArgsDict(
                {
                    "user": "sol",
                    "gossip": svmkit.firedancer.ConfigGossipArgsDict({
                        "host": node.instance.private_ip,
                        "entrypoints": entry_point,
                    }),
                    "layout": svmkit.firedancer.ConfigLayoutArgsDict({
                        "affinity": "auto",
                        "agave_affinity": "auto",
                        "bank_tile_count": 2,
                        "verify_tile_count": 1,

                    }),
                    "consensus": svmkit.firedancer.ConfigConsensusArgsDict({
                        "known_validators": known_validators,
                        "expected_genesis_hash": expected_genesis_hash,
                        "identity_path": "/home/sol/validator-keypair.json",
                        "vote_account_path": "/home/sol/vote-account-keypair.json",
                        "wait_for_vote_to_start_leader": False,
                    }),
                    "ledger": svmkit.firedancer.ConfigLedgerArgsDict({
                        "path": "/home/sol/ledger",
                        "accounts_path": "/home/sol/accounts",
                    }),
                    "rpc": svmkit.firedancer.ConfigRPCArgsDict({
                        "port": RPC_PORT,
                    }),
                    "extra_config": [
                        """
[development]
  [development.gossip]
     allow_private_address = true
"""
                    ]
                }
            ),
            environment=sol_env,
            opts=pulumi.ResourceOptions(
                depends_on=[node.instance, bootstrap_validator])
        )
    else:
        raise ValueError("Unknown validator kind")

    transfer = svmkit.account.Transfer(node.name + "-transfer",
                                       connection=bootstrap_node.connection,
                                       transaction_options={
                                           "key_pair": treasury_key.json,
                                       },
                                       amount=100,
                                       recipient_pubkey=node.validator_key.public_key,
                                       allow_unfunded_recipient=True,
                                       opts=pulumi.ResourceOptions(depends_on=[bootstrap_validator]))

    vote_account = svmkit.account.VoteAccount(node.name + "-voteAccount",
                                              connection=bootstrap_node.connection,
                                              key_pairs={
                                                  "identity": node.validator_key.json,
                                                  "vote_account": node.vote_account_key.json,
                                                  "auth_withdrawer": treasury_key.json,
                                              },
                                              opts=pulumi.ResourceOptions(depends_on=[transfer]))

    stake_account_key = svmkit.KeyPair(node.name + "-stakeAccount-key")
    svmkit.account.StakeAccount(node.name + "-stakeAccount",
                                connection=bootstrap_node.connection,
                                transaction_options={
                                    "key_pair": treasury_key.json,
                                },
                                key_pairs={
                                    "stake_account": stake_account_key.json,
                                    "vote_account": node.vote_account_key.json,
                                },
                                amount=10,
                                opts=pulumi.ResourceOptions(depends_on=[vote_account]))

watchtower_notifications: svmkit.watchtower.NotificationConfigArgsDict = {}

if slack_webhook_url:
    watchtower_notifications["slack"] = cast(svmkit.watchtower.SlackConfigArgsDict, {
        "webhookUrl": slack_webhook_url
    })

if discord_webhook_url:
    watchtower_notifications["discord"] = cast(svmkit.watchtower.DiscordConfigArgsDict, {
        "webhookUrl": discord_webhook_url
    })

if telegram_bot_token and telegram_chat_id:
    watchtower_notifications["telegram"] = cast(svmkit.watchtower.TelegramConfigArgsDict, {
        "botToken": telegram_bot_token,
        "chatId": telegram_chat_id
    })

if pagerduty_integration_key:
    watchtower_notifications["pager_duty"] = cast(svmkit.watchtower.PagerDutyConfigArgsDict, {
        "integrationKey": pagerduty_integration_key
    })

if twilio_account_sid and twilio_auth_token and twilio_to_number and twilio_from_number:
    watchtower_notifications["twilio"] = cast(svmkit.watchtower.TwilioConfigArgsDict, {
        "accountSid": twilio_account_sid,
        "authToken": twilio_auth_token,
        "toNumber": twilio_to_number,
        "fromNumber": twilio_from_number
    })

watchtower = svmkit.watchtower.Watchtower(
    'bootstrap-watchtower',
    connection=bootstrap_node.connection,
    environment=sol_env,
    flags={
        "validator_identity": [node.validator_key.public_key for node in all_nodes],
    },
    notifications=watchtower_notifications,
    opts=pulumi.ResourceOptions(depends_on=[bootstrap_validator])
)

tuner_variant_name = tuner_config.get("variant") or "generic"
tuner_variant = svmkit.tuner.TunerVariant(tuner_variant_name)

generic_tuner_params_output = svmkit.tuner.get_default_tuner_params_output(
    variant=tuner_variant)

params = generic_tuner_params_output.apply(lambda p: cast(svmkit.tuner.TunerParamsArgsDict, {
    "cpu_governor": p.cpu_governor,
    "kernel": p.kernel,
    "net": p.net,
    "vm": p.vm,
}))

pulumi.export("tuner_params", params)

for node in all_nodes:
    tuner = svmkit.tuner.Tuner(
        node.name + "-tuner",
        connection=node.connection,
        params=params,
        opts=pulumi.ResourceOptions(depends_on=([node.instance]))
    )

pulumi.export("nodes_name", [x.name for x in all_nodes])
pulumi.export("nodes_public_ip", [x.instance.public_ip for x in all_nodes])
pulumi.export("nodes_private_key", [
              x.ssh_key.private_key_openssh for x in all_nodes])

pulumi.export("speInfo",
              {
                  "treasuryKey": treasury_key,
                  "bootstrap": {
                      "connection": bootstrap_node.connection
                  },
                  "otherValidators": [{"voteAccountKey": node.vote_account_key} for node in nodes],
              })
