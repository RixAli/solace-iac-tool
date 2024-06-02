import click
from iac.aws_vm import AwsVM
from iac.aws_network import AwsNetwork
from iac.aws_rds_db import AwsRdsDB
from util.iac_util import load_yaml, check_aws_cli_login


@click.group()
def cli():
    """CLI tool for managing AWS resources."""
    pass


@click.command()
@click.argument('config', type=click.Path(exists=True))
def vm(config):
    """Manage AWS Virtual Machines.

    Arguments:
    config -- Path to the YAML configuration file for the VM.
    """
    check_aws_cli_login()
    config_data = load_yaml(config)
    aws_vm = AwsVM(config_data)
    if aws_vm.verify_config():
        vm_id = aws_vm.apply()
        click.echo(f"Changes applied on VM ID: {vm_id}")
    else:
        click.echo("VM configuration verification failed.", err=True)


@click.command()
@click.argument('config', type=click.Path(exists=True))
def network(config):
    """Manage AWS Networks.

    Arguments:
    config -- Path to the YAML configuration file for the network.
    """
    check_aws_cli_login()
    config_data = load_yaml(config)
    aws_network = AwsNetwork(config_data)
    if aws_network.verify_config():
        network_info = aws_network.create_network()
        click.echo(f"VPC created with ID: {network_info['VpcId']}")
        click.echo(f"Public Subnet created with ID: {network_info['PublicSubnetId']}")
        click.echo(f"Private Subnet created with ID: {network_info['PrivateSubnetId']}")
        click.echo(f"Internet Gateway created with ID: {network_info['InternetGatewayId']}")
    else:
        click.echo("Network configuration verification failed.", err=True)


@click.command()
@click.argument('config', type=click.Path(exists=True))
def db(config):
    """Manage AWS RDS Databases.

    Arguments:
    config -- Path to the YAML configuration file for the database.
    """
    check_aws_cli_login()
    config_data = load_yaml(config)
    aws_rds_db = AwsRdsDB(config_data)
    if aws_rds_db.verify_config():
        db_id = aws_rds_db.apply()
        click.echo(f"Changes applied on Database with ID: {db_id}")
    else:
        click.echo("DB configuration verification failed.", err=True)


cli.add_command(vm)
cli.add_command(network)
cli.add_command(db)

if __name__ == '__main__':
    cli()
