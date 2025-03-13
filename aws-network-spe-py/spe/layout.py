from typing import Literal, Optional

# Default version for Firedancer validator
FIREDANCER_VERSION = "0.305.20111-2"

# Default instance type for Firedancer validator
FIREDANCER_INSTANCE_TYPE = "r7a.8xlarge"

# Default version for Agave validator
AGAVE_VERSION = "2.1.13-1"

# Default instance type for Agave validator
AGAVE_INSTANCE_TYPE = "c6i.xlarge"

ValidatorKind = Literal["agave", "firedancer"]


class ValidatorLayout:
    def __init__(self, kind: ValidatorKind, version: str, instance_type: str):
        self.kind = kind
        self.version = version
        self.instance_type = instance_type


class AgaveLayout(ValidatorLayout):
    def __init__(self, version: Optional[str], instance_type: Optional[str]):
        version = version if version is not None else AGAVE_VERSION
        instance_type = instance_type if instance_type is not None else AGAVE_INSTANCE_TYPE

        super().__init__("agave", version, instance_type)


class FiredancerLayout(ValidatorLayout):
    def __init__(self, version: Optional[str], instance_type: Optional[str]):
        version = version if version is not None else FIREDANCER_VERSION
        instance_type = instance_type if instance_type is not None else FIREDANCER_INSTANCE_TYPE

        super().__init__("firedancer", version, instance_type)
