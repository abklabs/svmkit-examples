import pulumi
import pulumi_aws as aws

stack_name = pulumi.get_stack()

external_sg = aws.ec2.SecurityGroup(
    "external-access",
    description="Allow external SSH access to all of the nodes",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 0,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    tags={
        "Stack": stack_name,
    }
)

internal_sg = aws.ec2.SecurityGroup(
    "internal-access",
    description="Permissive internal traffic",
    ingress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "self": True},
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    tags={
        "Stack": stack_name,
    }
)
