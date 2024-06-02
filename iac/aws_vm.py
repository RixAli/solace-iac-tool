import boto3


class AwsVM:

    def __init__(self, config):
        if 'vm' in config:
            self.config = config['vm']
        else:
            self.config = None

    def verify_config(self):
        required_keys = ['instance_type', 'ami_id', 'key_name']
        # optional_keys = ['security_group_ids', 'subnet_id', 'instance_id']
        if not self.config:
            print(f"Could not find VM configuration")
            return False
        for key in required_keys:
            if key not in self.config:
                print(f"Missing required key in VM config: {key}")
                return False
        return True

    def apply(self):
        if 'instance_id' in self.config:
            return self.__update_vm()
        else:
            return self.__create_vm()

    def __create_vm(self):
        ec2 = boto3.resource('ec2')
        instance_params = {
            'InstanceType': self.config['instance_type'],
            'ImageId': self.config['ami_id'],
            'KeyName': self.config['key_name'],
            'MinCount': 1,
            'MaxCount': 1
        }

        if 'subnet_id' in self.config:
            instance_params['SubnetId'] = self.config['subnet_id']

        if 'security_group_ids' in self.config:
            instance_params['SecurityGroupIds'] = self.config['security_group_ids']

        instances = ec2.create_instances(**instance_params)
        return instances[0].id

    def __update_vm(self):
        ec2 = boto3.client('ec2')

        instance_id = self.config['instance_id']
        instance = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]

        if 'instance_type' in self.config and self.config['instance_type'] != instance['InstanceType']:
            ec2.stop_instances(InstanceIds=[instance_id])
            waiter = ec2.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[instance_id])
            ec2.modify_instance_attribute(InstanceId=instance_id, InstanceType={'Value': self.config['instance_type']})
            ec2.start_instances(InstanceIds=[instance_id])
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])
        else:
            print(f"No update found in vm {self.config['instance_id']}. Only Instance Type of the VM can be updated")

        return instance_id
