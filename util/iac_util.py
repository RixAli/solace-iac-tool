import yaml
import sys
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def load_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)


def check_aws_cli_login():
    """
    Checks if AWS CLI is configured with valid credentials.
    If not, throw exception.
    """
    try:
        # Try to create a session to check if credentials are configured
        boto3.Session().client('sts').get_caller_identity()
        print("AWS login session found.")
    except (NoCredentialsError, PartialCredentialsError):
        print(
            """AWS login session Not found.
Log into AWS using AWS CLI, use command: aws configure"""
        )

