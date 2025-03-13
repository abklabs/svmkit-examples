
from typing import Union
from spe.node import Node
import pulumi
import pulumi_svmkit as svmkit


class Firedancer(pulumi.ComponentResource):
    def __init__(self, name: str, node: Node, version: str | None, config: svmkit.firedancer.ConfigArgsDict, environment: Union[svmkit.solana.EnvironmentArgs, svmkit.solana.EnvironmentArgsDict], opts: pulumi.ResourceOptions | None = None) -> None:
        super().__init__('svmkit-examples:spe:Firedancer', name, None, opts)

        svmkit.validator.Firedancer(
            name + "-firedancer-validator",
            environment=environment,
            connection=node.connection,
            version=version,
            key_pairs={
                "identity": node.validator_key.json,
                "vote_account": node.vote_account_key.json,
            },
            config=config,
            opts=pulumi.ResourceOptions(parent=self)
        )
