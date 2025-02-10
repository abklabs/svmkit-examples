from typing import TypedDict, Literal
from .node import *
from .agave import *
from .firedancer import *

ValidatorKind = Literal["agave", "firedancer"]


class ValidatorLayout(TypedDict):
    kind: ValidatorKind
    version: str | None


GOSSIP_PORT = 8001
RPC_PORT = 8899
FAUCET_PORT = 9900
