import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
import pulumi_svmkit as svmkit

from spe import Node, Genesis, Info

total_nodes = 3

bootstrap_node = Node("bootstrap-node")
genesis = Genesis(bootstrap_node)

gossip_port = 8001
rpc_port = 8899

sol_env = svmkit.solana.EnvironmentArgs(
    rpc_url=bootstrap_node.instance.private_ip.apply(
        lambda ip: f"http://{ip}:{rpc_port}")
)

base_flags = svmkit.agave.FlagsArgsDict({
    "only_known_rpc": False,
    "rpc_port": rpc_port,
    "dynamic_port_range": "8002-8020",
    "private_rpc": False,
    "gossip_port": gossip_port,
    "rpc_bind_address": "0.0.0.0",
    "wal_recovery_mode": "skip_any_corrupted_record",
    "limit_ledger_size": 50000000,
    "block_production_method": "central-scheduler",
    "full_snapshot_interval_slots": 1000,
    "no_wait_for_vote_to_start_leader": True,
    "use_snapshot_archives_at_startup": "when-newest",
    "allow_private_addr": True,
})

bootstrap_flags = base_flags.copy()
bootstrap_flags.update({
    "full_rpc_api": True,
    "no_voting": False,
    "gossip_host": bootstrap_node.instance.private_ip,
})

bootstrap_validator = bootstrap_node.configure_validator(
    bootstrap_flags, environment=sol_env, depends_on=[genesis.genesis])

nodes = [Node(f"node{n}") for n in range(total_nodes - 1)]
all_nodes = [bootstrap_node] + nodes

for node in nodes:
    other_nodes = [x for x in all_nodes if x != node]
    entry_point = [x.instance.private_ip.apply(
        lambda v: f"{v}:{gossip_port}") for x in other_nodes]

    flags = base_flags.copy()
    flags.update({
        "entry_point": entry_point,
        "known_validator": [x.validator_key.public_key for x in other_nodes],
        "expected_genesis_hash": genesis.genesis.genesis_hash,
        "full_rpc_api": node == bootstrap_node,
        "gossip_host": node.instance.private_ip,
    })

    node.configure_validator(flags, environment=sol_env,
                             depends_on=[bootstrap_validator])

info = Info(genesis, other_validators=nodes)

pulumi.export("nodes_public_ip", [x.instance.public_ip for x in all_nodes])
pulumi.export("nodes_private_key", [
              x.ssh_key.private_key_openssh for x in all_nodes])

pulumi.export("speInfo", info.get_info())
