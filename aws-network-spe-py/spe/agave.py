from typing import Union
from spe.node import Node
import pulumi
import pulumi_svmkit as svmkit


class Agave(pulumi.ComponentResource):
    def __init__(self, name: str, node: Node, version: str | None, flags: svmkit.agave.FlagsArgsDict, environment: Union['svmkit.solana.EnvironmentArgs', 'svmkit.solana.EnvironmentArgsDict'], startup_policy: Union['svmkit.agave.StartupPolicyArgs', 'svmkit.agave.StartupPolicyArgsDict'],  opts: pulumi.ResourceOptions | None = None) -> None:
        super().__init__('svmkit-examples:spe:Agave', name, None, opts)

        svmkit.validator.Agave(
            name + "-agave-validator",
            environment=environment,
            connection=node.connection,
            version=version,
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
                "rpc_service_timeout": 360,
            },
            info={
                "name": name,
                "details": "An AWS network-based SPE validator node.",
            },
            opts=pulumi.ResourceOptions(parent=self)
        )
