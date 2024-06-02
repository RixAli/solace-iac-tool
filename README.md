# AWS Infrastructure Automation CLI

This CLI tool is designed to create AWS resources; Virtual Machines, Networks, and RDS Databases. It uses YAML configuration files to define the resources and their properties, and requires AWS CLI authentication.

## Installation
Python, pip and AWS cli is required. 
Install dependencies:
```sh
   pip install -r requirements.txt
```
AWS cli will be used to create login session needed to use aws api.
To authenticate run
```sh
   aws configure
```



## Usage

To create resource pass name of the resource with configuration file to the iac.py script.

```sh
   python iac.py vm config/vm_sample.yaml
   python iac.py db config/db_sample.yaml
   python iac.py network config/network_sample.yaml
```



## Design

We use AWS python SDK to create a very simple cli tool. the tool creates VM (EC2) instances, databases (RDS) and network configuration(VPC, IGW and Subnets).
The code for IAC can be found in iac package.

The vm can be created and updated (applied). Only the instance type can be updated and the configuration file requires the instance ID to perform an update. 
The db can be applied as well. Only instance class and allocated storage can be updated.

The network does not support update, It can be only created.

The config has sample config files with values, that work for free tier.