import boto3


class AwsNetwork:

    def __init__(self, config):
        if 'network' in config:
            self.config = config['network']
        else:
            self.config = None

    def verify_config(self):
        required_keys = ['vpc_cidr', 'public_subnet_cidr', 'private_subnet_cidr', 'availability_zone',
                         'public_subnet_name', 'private_subnet_name']
        if not self.config:
            print(f"Could not find Network configuration")
            return False
        for key in required_keys:
            if key not in self.config:
                print(f"Missing required key in Network config: {key}")
                return False
        return True

    def create_network(self):
        ec2 = boto3.client('ec2')

        # create VPC
        vpc_response = ec2.create_vpc(
            CidrBlock=self.config['vpc_cidr']
        )
        vpc_id = vpc_response['Vpc']['VpcId']

        # create igw for public subnet and attach igw to vpc
        igw_response = ec2.create_internet_gateway(
        )
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

        # create public subnet in vpc
        public_subnet_response = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=self.config['public_subnet_cidr'],
            AvailabilityZone=self.config['availability_zone'],
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [{'Key': 'Name', 'Value': self.config['public_subnet_name']}]
                }
            ]
        )
        public_subnet_id = public_subnet_response['Subnet']['SubnetId']

        # create private subnet in vpc
        private_subnet_response = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=self.config['private_subnet_cidr'],
            AvailabilityZone=self.config['availability_zone'],
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [{'Key': 'Name', 'Value': self.config['private_subnet_name']}]
                }
            ]
        )
        private_subnet_id = private_subnet_response['Subnet']['SubnetId']

        # Add route table for public subnet
        public_route_table_response = ec2.create_route_table(
            VpcId=vpc_id
        )
        public_route_table_id = public_route_table_response['RouteTable']['RouteTableId']
        ec2.create_route(
            RouteTableId=public_route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )
        ec2.associate_route_table(RouteTableId=public_route_table_id, SubnetId=public_subnet_id)
        ec2.modify_subnet_attribute(
            SubnetId=public_subnet_id,
            MapPublicIpOnLaunch={'Value': True}
        )

        return {
            'VpcId': vpc_id,
            'PublicSubnetId': public_subnet_id,
            'PrivateSubnetId': private_subnet_id,
            'InternetGatewayId': igw_id
        }
