""" A simple Solana Proving Environment (SPE) using Pulumi and SVMKit. """

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
import pulumi_svmkit as svmkit

from spe import Node, BootstrapNode, ValidatorNode, FaucetNode

node_config = pulumi.Config("node")

# --- consts ---

GOSSIP_PORT = 8001
RPC_PORT = 8899
FAUCET_PORT = 9900

total_nodes = node_config.get_int("count") or 3

# --- create base nodes ---

bootstrap_node = BootstrapNode(
    name="bootstrap-node",
    config=node_config,
    gossip_port=GOSSIP_PORT,
    rpc_port=RPC_PORT,
)

faucet_node = FaucetNode(
    name="faucet-node",
    config=node_config,
)

# --- flags and environment ---

rpc_faucet_address = faucet_node.instance.private_ip.apply(
    lambda ip: f"{ip}:{FAUCET_PORT}"
)

sol_env = svmkit.solana.EnvironmentArgs(
    rpc_url=bootstrap_node.instance.private_ip.apply(
        lambda ip: f"http://{ip}:{RPC_PORT}"
    )
)

bootstrap_flags = bootstrap_node.get_validator_flags(
    {
        "full_rpc_api": True,
        "no_voting": False,
        "gossip_host": bootstrap_node.instance.private_ip,
        "extra_flags": [
            # Enabled so that Solana Explorer has
            # the data it needs.
            "--enable-extended-tx-metadata-storage",
            "--enable-rpc-transaction-history",
        ],
        "rpc_faucet_address": rpc_faucet_address,
    }
)

# --- configure base nodes ---

faucet_node.configure_faucet(depends_on=[])

bootstrap_genesis = bootstrap_node.configure_genesis(
    faucet_key=faucet_node.faucet_key, depends_on=[faucet_node.instance]
)

bootstrap_validator = bootstrap_node.configure_validator(
    flags=bootstrap_flags,
    environment=sol_env,
    startup_policy={"wait_for_rpc_health": True},
    depends_on=[bootstrap_genesis],
)

# --- configure validator nodes ---

nodes = []
for i in range(total_nodes - 1):
    node = ValidatorNode(
        name=f"validator-node-{i}",
        config=node_config,
    )
    nodes.append(node)

all_nodes = [bootstrap_node] + nodes

for node in nodes:
    other_nodes = [x for x in all_nodes if x != node]
    entry_point = [
        x.instance.private_ip.apply(lambda v: f"{v}:{GOSSIP_PORT}") for x in other_nodes
    ]

    node_flags = node.get_validator_flags(
        {
            "entry_point": entry_point,
            "known_validator": [x.validator_key.public_key for x in other_nodes],
            "expected_genesis_hash": bootstrap_genesis.genesis_hash,
            "full_rpc_api": node == bootstrap_node,
            "gossip_host": node.instance.private_ip,
            "rpc_faucet_address": rpc_faucet_address,
        }
    )

    node.configure_validator(
        flags=node_flags,
        environment=sol_env,
        startup_policy=svmkit.agave.StartupPolicyArgs(),
        depends_on=[bootstrap_validator],
    )

    transfer = svmkit.account.Transfer(
        node.name + "-transfer",
        connection=bootstrap_node.connection,
        transaction_options={
            "key_pair": bootstrap_node.treasury_key.json,
        },
        amount=100,
        recipient_pubkey=node.validator_key.public_key,
        allow_unfunded_recipient=True,
        opts=pulumi.ResourceOptions(depends_on=[bootstrap_validator]),
    )

    vote_account = svmkit.account.VoteAccount(
        node.name + "-voteAccount",
        connection=bootstrap_node.connection,
        key_pairs={
            "identity": node.validator_key.json,
            "vote_account": node.vote_account_key.json,
            "auth_withdrawer": bootstrap_node.treasury_key.json,
        },
        opts=pulumi.ResourceOptions(depends_on=[transfer]),
    )

    stake_account_key = svmkit.KeyPair(node.name + "-stakeAccount-key")
    svmkit.account.StakeAccount(
        node.name + "-stakeAccount",
        connection=bootstrap_node.connection,
        transaction_options={
            "key_pair": bootstrap_node.treasury_key.json,
        },
        key_pairs={
            "stake_account": stake_account_key.json,
            "vote_account": node.vote_account_key.json,
        },
        amount=150,
        opts=pulumi.ResourceOptions(depends_on=[vote_account]),
    )

export_nodes: list[Node] = [bootstrap_node, faucet_node] + nodes

pulumi.export("nodes_name", [x.name for x in export_nodes])
pulumi.export("nodes_public_ip", [x.instance.public_ip for x in export_nodes])
pulumi.export(
    "nodes_private_key", [x.ssh_key.private_key_openssh for x in export_nodes]
)

pulumi.export(
    "speInfo",
    {
        "treasuryKey": bootstrap_node.treasury_key,
        "faucetKey": faucet_node.faucet_key,
        "bootstrap": {"connection": bootstrap_node.connection},
        "faucet": {"connection": faucet_node.connection},
        "otherValidators": [
            {"voteAccountKey": node.vote_account_key} for node in nodes
        ],
    },
)
