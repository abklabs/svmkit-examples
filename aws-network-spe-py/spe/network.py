import pulumi
import pulumi_aws as aws

network_config = pulumi.Config("network")
vpc_id = network_config.get('vpcId') or None

if vpc_id:
    subnets = aws.ec2.get_subnets(
        filters=[{
            "name": "vpc-id",
            "values": [vpc_id],
        }],
    )

    if len(subnets.ids) < 1:
        raise ValueError("VPC is required to have at least 1 subnet.")

    subnet_id = subnets.ids[0]
else:
    subnet_id = None

stack_name = pulumi.get_stack()

external_sg = aws.ec2.SecurityGroup(
    "external-access",
    description="Allow external SSH access to all of the nodes",
    vpc_id=vpc_id,
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
    vpc_id=vpc_id,
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
