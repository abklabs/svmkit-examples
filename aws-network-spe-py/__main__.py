import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
import pulumi_svmkit as svmkit
from typing import cast


from spe import Node, AGAVE_VERSION

GOSSIP_PORT = 8001
RPC_PORT = 8899
FAUCET_PORT = 9900

node_config = pulumi.Config("node")

total_nodes = node_config.get_int("count") or 3

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
        "bootstrap_validators": [
            {
                "identity_pubkey": bootstrap_node.validator_key.public_key,
                "vote_pubkey": bootstrap_node.vote_account_key.public_key,
                "stake_pubkey": stake_account_key.public_key,
            }
        ],
        "ledger_path": "/home/sol/ledger",
        "faucet_pubkey": faucet_key.public_key,
        "bootstrap_validator_stake_lamports": 10000000000,  # 10 SOL
        "enable_warmup_epochs": True,
        "slots_per_epoch": 8192,
        "cluster_type": "development",
        "faucet_lamports": 1000,
        "target_lamports_per_signature": 0,
        "inflation": "none",
        "lamports_per_byte_year": 1
    },
    primordial=[
        {
            "pubkey": bootstrap_node.validator_key.public_key,
            "lamports": 1000000000000,  # 1000 SOL
        },
        {
            "pubkey": treasury_key.public_key,
            "lamports": 100000000000000,  # 100000 SOL
        },
        {
            "pubkey": faucet_key.public_key,
            "lamports": 1000000000000,  # 1000 SOL
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

base_flags = svmkit.agave.FlagsArgsDict({
    "only_known_rpc": False,
    "rpc_port": RPC_PORT,
    "dynamic_port_range": "8002-8020",
    "private_rpc": False,
    "gossip_port": GOSSIP_PORT,
    "rpc_bind_address": "0.0.0.0",
    "wal_recovery_mode": "skip_any_corrupted_record",
    "limit_ledger_size": 50000000,
    "block_production_method": "central-scheduler",
    "full_snapshot_interval_slots": 1000,
    "no_wait_for_vote_to_start_leader": True,
    "use_snapshot_archives_at_startup": "when-newest",
    "allow_private_addr": True,
    "rpc_faucet_address": rpc_faucet_address,
})

bootstrap_flags = base_flags.copy()
bootstrap_flags.update({
    "full_rpc_api": True,
    "no_voting": False,
    "gossip_host": bootstrap_node.instance.private_ip,
    "extra_flags": [
        "--enable-extended-tx-metadata-storage",  # Enabled so that
        "--enable-rpc-transaction-history",      # Solana Explorer has
                                                 # the data it needs.
    ]
})

faucet = svmkit.faucet.Faucet(
    "bootstrap-faucet",
    connection=bootstrap_node.connection,
    keypair=faucet_key.json,
    flags={
        "per_request_cap": 1000,
    },
    opts=pulumi.ResourceOptions(depends_on=([genesis])))

bootstrap_validator = bootstrap_node.configure_validator(
    bootstrap_flags, environment=sol_env, startup_policy={
        "wait_for_rpc_health": True},
    depends_on=[faucet])

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
    opts=pulumi.ResourceOptions(depends_on=([bootstrap_validator])))

nodes = [Node(f"node{n}") for n in range(total_nodes - 1)]
all_nodes = [bootstrap_node] + nodes

for node in nodes:
    other_nodes = [x for x in all_nodes if x != node]
    entry_point = [x.instance.private_ip.apply(
        lambda v: f"{v}:{GOSSIP_PORT}") for x in other_nodes]

    flags = base_flags.copy()
    flags.update({
        "entry_point": entry_point,
        "known_validator": [x.validator_key.public_key for x in other_nodes],
        "expected_genesis_hash": genesis.genesis_hash,
        "full_rpc_api": node == bootstrap_node,
        "gossip_host": node.instance.private_ip,
    })

    validator = node.configure_validator(flags, environment=sol_env, startup_policy=svmkit.agave.StartupPolicyArgs(),
                                         depends_on=[bootstrap_validator])

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
                                              opts=pulumi.ResourceOptions(depends_on=([transfer])))

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
                                opts=pulumi.ResourceOptions(depends_on=([vote_account])))

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
    opts=pulumi.ResourceOptions(depends_on=([bootstrap_validator]))
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
    "fs": p.fs,
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
