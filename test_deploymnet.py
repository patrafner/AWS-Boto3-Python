from src.ec2.vpc import VPC
from src.ec2.ec2 import EC2
from src.client_locator import EC2Client

def main():
    #create a vpc
    ec2_client = EC2Client().get_client()
    vpc = VPC(ec2_client)

    vpc_response = vpc.create_vpc()

    print("VPC created:" + str(vpc_response))

    #add name tag to VPC
    vpc_name = "Boto3-VPC"
    vpc_id = vpc_response["Vpc"]["VpcId"]
    vpc.add_name_tag(vpc_id, vpc_name)

    print("Added " + vpc_name + " to " + vpc_id)

    #Create IGW
    igw_response = vpc.create_internet_gateway()

    #to attach IGW to VPC then see methof in vpc file
    igw_id = igw_response["InternetGateway"]["InternetGatewayId"]

    vpc.attach_igw_to_vpc(vpc_id, igw_id)

    #create a public subnet
    public_subnet_reponse = vpc.create_subnet(vpc_id, "10.0.1.0/24")
    public_subnet_id = public_subnet_reponse["Subnet"]["SubnetId"]
    print("Subnet created for VPC " + vpc_id + ":" + str(public_subnet_reponse))

    #add name tag to public subnet
    vpc.add_name_tag(public_subnet_id, "Boto3-Public-Subnet")

    #create a public route table
    public_route_table_response = vpc.create_public_route_table(vpc_id)

    rtb_id = public_route_table_response["RouteTable"]["RouteTableId"]

    #Adding IGW to the public route table
    vpc.create_igw_route_to_public_route_table(rtb_id, igw_id)

    #Associate public subnet to route table
    vpc.associate_subnet_with_route_table(public_subnet_id, rtb_id)

    #allow auto assign public ip addresses for subnet
    vpc.allow_auto_assign_ip_addresses_for_subnet(public_subnet_id)

    #create a private subnet
    private_subnet_response =  vpc.create_subnet(vpc_id, "10.0.2.0/24")
    private_subnet_id = private_subnet_response["Subnet"]["SubnetId"]
    print("Created private subnet " + private_subnet_id + " for VPC " + vpc_id)

    #add name tag to private subnet
    vpc.add_name_tag(private_subnet_id, "Boto3-Private-Subnet")


    #EC2 instnaces remmeber ec2_client is the client for VPC.
    ec2 = EC2(ec2_client)

    #create keypair.
    key_pair_name = "Boto3-Keypair"
    key_pair_response = ec2.create_key_pair(key_pair_name)
    print("Created Key Pair with Name " + key_pair_name + ":" + str(key_pair_response))

    #create a security group
    public_security_group_name = "Boto3-Public-SG"
    public_security_group_descritpion = "Public Security Group for Public Subnet Internet Access"
    public_security_group_response = ec2.create_security_group(public_security_group_name, public_security_group_descritpion, vpc_id)
    public_security_group_id = public_security_group_response["GroupId"]

    # add public access to SG
    ec2.add_inbound_rule_to_sg(public_security_group_id)
    print("Added public access rule to SG " + public_security_group_name)

    # create startup script
    user_data = """#!/bin/bash
                yum update -y
                yum install httpd24 -y
                service httpd start
                chkconfig httpd on
                echo "<html><body><h1>Hello from <b>Boto3</b> using python!</h1></body></html>" > /var/www/html/index.html"""


    #launch public instance
    ami_id = "ami-1b316af0"
    ec2.launch_ec2_instance(ami_id, key_pair_name, 1, 1, public_security_group_id, public_subnet_id, user_data)
    print("Launching public EC2 instance using AMI 1b316af0")

    #for private instance
    #adding another security group for private ec2 instance
    private_security_group_name = "Boto3-Private_SG"
    private_security_group_description = "Private Security Group for Private Subnet"
    private_security_group_response = ec2.create_security_group(private_security_group_name, private_security_group_description, vpc_id)
    private_security_group_id = private_security_group_response["GroupId"]

    #adding rule to SG
    ec2.add_inbound_rule_to_sg(private_security_group_id)

    #launch instance
    ec2.launch_ec2_instance(ami_id, key_pair_name, 1, 1, private_security_group_id, private_subnet_id, """""")


def describe_instances():
    ec2_client = EC2Client().get_client()
    #get the ec2 reference
    ec2 = EC2(ec2_client)
    ec2_response = ec2.describe_ec2_instance()
    print(str(ec2_response))


def modify_instance():
    ec2_client = EC2Client().get_client()
    # get the ec2 reference
    ec2 = EC2(ec2_client)
    ec2_response = ec2.modify_ec2_instances("i-054f9e6c3b56d49d1")

def stop_instance():
    ec2_client = EC2Client().get_client()
    # get the ec2 reference
    ec2 = EC2(ec2_client)
    ec2.stop_instance("i-0cce30cf2bcacf627")


def start_instance():
    ec2_client = EC2Client().get_client()
    # get the ec2 reference
    ec2 = EC2(ec2_client)
    ec2.start_instance("i-0cce30cf2bcacf627")


def terminate_instance():
    ec2_client = EC2Client().get_client()
    # get the ec2 reference
    ec2 = EC2(ec2_client)
    ec2.terminate_instance("i-0cce30cf2bcacf627")


if __name__ == "__main__":
    #main()
    #describe_instances()
    #modify_instance()
    #stop_instance()
    #start_instance()
    terminate_instance()
# we put #infront of main it will only execute the functions that you specify below like describe_instances