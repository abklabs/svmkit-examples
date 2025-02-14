from typing import Literal
from .node import *
from .agave import *
from .firedancer import *

ValidatorKind = Literal["agave", "firedancer"]


class ValidatorLayout:
    def __init__(self, kind: ValidatorKind, version: str | None, instance_type: str):
        self.kind = kind
        self.version = version
        self.instance_type = instance_type


class AgaveLayout(ValidatorLayout):
    def __init__(self, version: str | None, instance_type: str | None):
        version = version if version is not None else AGAVE_VERSION
        instance_type = instance_type if instance_type is not None else AGAVE_DEFAULT_INSTANCE_TYPE

        super().__init__("agave", version, instance_type)


class FiredancerLayout(ValidatorLayout):
    def __init__(self, version: str | None, instance_type: str | None):
        version = version if version is not None else FIREDANCER_VERSION
        instance_type = instance_type if instance_type is not None else FIREDANCER_DEFAULT_INSTANCE_TYPE

        super().__init__("firedancer", version, instance_type)


GOSSIP_PORT = 8001
RPC_PORT = 8899
FAUCET_PORT = 9900
