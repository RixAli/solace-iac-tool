import boto3
from botocore.exceptions import ClientError


class AwsRdsDB:

    def __init__(self, config):
        if 'rds' in config:
            self.config = config['rds']
        else:
            self.config = None

    def verify_config(self):
        required_keys = ['db_instance_identifier', 'db_instance_class', 'engine', 'master_username',
                         'master_user_password']
        if not self.config:
            print(f"Could not find DB configuration")
            return False
        for key in required_keys:
            if key not in self.config:
                print(f"Missing required key in DB config: {key}")
                return False
        return True

    def apply(self):
        instance = self.__update_db()
        if not instance:
            return self.__create_db()
        else:
            return instance

    def __create_db(self):
        rds = boto3.client('rds')
        db_instance = rds.create_db_instance(
            DBInstanceIdentifier=self.config['db_instance_identifier'],
            AllocatedStorage=self.config['allocated_storage'] if 'allocated_storage' in self.config else 20,
            DBInstanceClass=self.config['db_instance_class'],
            Engine=self.config['engine'],
            MasterUsername=self.config['master_username'],
            MasterUserPassword=self.config['master_user_password']
        )
        return db_instance['DBInstance']['DBInstanceIdentifier']

    def __update_db(self):
        rds = boto3.client('rds')
        db_instance_id = self.config['db_instance_identifier']

        try:
            response = rds.describe_db_instances(DBInstanceIdentifier=db_instance_id)
            db_instance = response['DBInstances'][0]
            print(f"Found database: {db_instance_id}")
        except ClientError as e:
            print(f"Failed to describe DB instance: {e}")
            return False
        modifications = {}

        if 'allocated_storage' in self.config and self.config['allocated_storage'] != db_instance['AllocatedStorage']:
            modifications['AllocatedStorage'] = self.config['allocated_storage']

        if 'db_instance_class' in self.config and self.config['db_instance_class'] != db_instance['DBInstanceClass']:
            modifications['DBInstanceClass'] = self.config['db_instance_class']

        if modifications:
            try:
                response = rds.modify_db_instance(
                    DBInstanceIdentifier=db_instance_id,
                    **modifications,
                    ApplyImmediately=True
                )
                return response['DBInstance']['DBInstanceIdentifier']
            except Exception as e:
                print(f"Failed to modify DB instance: {e}")
                return None
        else:
            print(f"No modifications needed in database: {db_instance_id}")
            return db_instance_id
