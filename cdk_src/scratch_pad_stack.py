from aws_cdk import (
    aws_ec2 as ec2,
    core
)

class ScratchPadStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        vpc = ec2.Vpc(
                self, "MyVpc",
                cidr="10.13.0.0/21",
                max_azs=2,
                nat_gateways=0,
                subnet_configuration=[
                    ec2.SubnetConfiguration(name="pubSubnet", cidr_mask=24, subnet_type=ec2.SubnetType.PUBLIC),
                ]
            )
        
        # Tag all VPC Resources
        core.Tag.add(vpc,key="Owner",value="KonStone",include_resource_types=[])

        # We are using the latest AMAZON LINUX AMI
        ami_id = ec2.AmazonLinuxImage(generation = ec2.AmazonLinuxGeneration.AMAZON_LINUX_2).get_image(self).image_id

        # Lets add a security group for port 80
        high_perf_sg = ec2.SecurityGroup(self,
            "web_sec_grp",
            vpc = vpc,
            description="Allow internet access from the world",
            allow_all_outbound = True
        )
        high_perf_sg.add_ingress_rule(ec2.Peer.any_ipv4(), 
            ec2.Port.tcp(22),
            "Allow internet access from the world."
        )
        high_perf_sg.add_ingress_rule(ec2.Peer.any_ipv4(),
            ec2.Port.icmp_ping(),
            "Allow ping in security group."
        )

        # Update your key-name
        ssh_key_name = "virk"

        # We define instance details here
        web_inst_01 = ec2.CfnInstance(self,
            "webinstance01",
            image_id = ami_id,
            instance_type = "t2.micro",
            monitoring = False,
            key_name = ssh_key_name,
            # tags = [{"key": "Name","value": "KonStone-Web-instance"}],
            block_device_mappings=[{
                "ebs" : { "volumeSize" : 25 },
                "deviceName" : "/dev/xvda",
                }],
            network_interfaces = [{
                "deviceIndex": "0",
                "associatePublicIpAddress": True,
                "subnetId": vpc.public_subnets[0].subnet_id,
                "groupSet": [high_perf_sg.security_group_id]
            }], #https: //github.com/aws/aws-cdk/issues/3419
            tags=[core.CfnTag(key="Name", value=f"KonStone-Stack")]
        )

        web_inst_02 = ec2.CfnInstance(self,
            "webinstance02",
            image_id = ami_id,
            instance_type = "t2.micro",
            monitoring = False,
            key_name = ssh_key_name,
            # tags = [{"key": "Name","value": "KonStone-Web-instance"}],
            # block_device_mappings=[{"deviceName":"/dev/xvda"}]
            block_device_mappings=[{
                "ebs" : { "volumeSize" : 25 },
                "deviceName" : "/dev/xvda",
                }],
            network_interfaces = [{
                "deviceIndex": "0",
                "associatePublicIpAddress": True,
                "subnetId": vpc.public_subnets[0].subnet_id,
                "groupSet": [high_perf_sg.security_group_id]
            }], #https: //github.com/aws/aws-cdk/issues/3419
            tags=[core.CfnTag(key="Name", value=f"KonStone-Stack")]
        )
        # https://docs.aws.amazon.com/cdk/api/latest/python/modules.html
        a1 = core.Fn.get_att(logical_name_of_resource="webinstance01",attribute_name="PublicIp")
        core.CfnOutput(self,
            "web_inst_01",
            value=a1.to_string(),
            description="Web Server Public IP")
