from typing import Optional, Sequence
from pulumi import Input, ComponentResource, ResourceOptions
import pulumi_svmkit as svmkit

from .node import Node
from .layout import ValidatorLayout
from .agave import Agave
from .firedancer import Firedancer

GOSSIP_PORT = 8001
RPC_PORT = 8899


class Validator(ComponentResource):
    def __init__(self, name: str, node: Node, layout: ValidatorLayout, entry_point: Input[Sequence[Input[str]]], expected_genesis_hash: Input[str], known_validators: Input[Sequence[Input[str]]], rpc_faucet_address: Input[str],  environment: svmkit.solana.EnvironmentArgs | svmkit.solana.EnvironmentArgsDict, full_rpc_api: bool = False, no_voting: bool = False, enable_extended_tx_metadata_storage: bool = False, enable_rpc_transaction_history: bool = False, wait_for_rpc_health: bool = False, opts: Optional[ResourceOptions] = None):
        super().__init__('svmkit-example:spe:Validator', name, None, opts)

        if layout.kind == "agave":
            self.validator = Agave(
                node.name,
                node=node,
                version=layout.version,
                flags=svmkit.agave.FlagsArgsDict({
                    "allow_private_addr": True,
                    "block_production_method": "central-scheduler",
                    "dynamic_port_range": "8002-8020",
                    "entry_point": entry_point,
                    "expected_genesis_hash": expected_genesis_hash,
                    "full_rpc_api": full_rpc_api,
                    "full_snapshot_interval_slots": 1000,
                    "gossip_host": node.instance.private_ip,
                    "gossip_port": GOSSIP_PORT,
                    "known_validator": known_validators,
                    "limit_ledger_size": 50000000,
                    "no_voting": no_voting,
                    "no_wait_for_vote_to_start_leader": True,
                    "only_known_rpc": False,
                    "private_rpc": False,
                    "rpc_bind_address": "0.0.0.0",
                    "rpc_faucet_address": rpc_faucet_address,
                    "rpc_port": RPC_PORT,
                    "use_snapshot_archives_at_startup": "when-newest",
                    "wal_recovery_mode": "skip_any_corrupted_record",
                    "enable_extended_tx_metadata_storage": enable_extended_tx_metadata_storage,
                    "enable_rpc_transaction_history": enable_rpc_transaction_history
                }),
                environment=environment,
                startup_policy=svmkit.agave.StartupPolicyArgsDict({
                    "wait_for_rpc_health": wait_for_rpc_health
                }),
                opts=ResourceOptions(parent=self)
            )
        elif layout.kind == "firedancer":
            self.validator = Firedancer(
                node.name,
                node=node,
                version=layout.version,
                config=svmkit.firedancer.ConfigArgsDict({
                    "user": "sol",
                    "gossip": svmkit.firedancer.ConfigGossipArgsDict({
                        "host": node.instance.private_ip,
                        "entrypoints": entry_point,
                    }),
                    "layout": svmkit.firedancer.ConfigLayoutArgsDict({
                        "affinity": "auto",
                        "agave_affinity": "auto",
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
                }),
                environment=environment,
                opts=ResourceOptions(parent=self)
            )
        else:
            raise ValueError("Unknown validator kind")

        self.register_outputs({
            "validator": self.validator,
        })
