from typing import Union, Dict, Any
from spe.node import Node
import pulumi
import pulumi_svmkit as svmkit

AGAVE_VERSION = "1.18.26-1"


class Agave(pulumi.ComponentResource):
    def __init__(self, name: str, node: Node, flags: svmkit.agave.FlagsArgsDict, environment: Union['svmkit.solana.EnvironmentArgs', 'svmkit.solana.EnvironmentArgsDict'], startup_policy: Union['svmkit.agave.StartupPolicyArgs', 'svmkit.agave.StartupPolicyArgsDict'], opts: pulumi.ResourceOptions = pulumi.ResourceOptions()) -> None:
        super().__init__('svmkit-examples:spe:Agave', name, None, opts)

        svmkit.validator.Agave(
            name,
            environment=environment,
            connection=node.connection,
            version=AGAVE_VERSION,
            startup_policy=startup_policy,
            shutdown_policy={
                "force": True,
            },
            key_pairs={
                "identity": node.validator_key.json,
                "vote_account": node.vote_account_key.json,
            },
            flags=flags,
            timeout_config={
                "rpc_service_timeout": 120,
            },
            info={
                "name": name,
                "details": "An AWS network-based SPE validator node.",
            },
            opts=opts
        )
