from aws_cdk import (
    aws_ssm as ssm,
    aws_iam as iam,
    aws_cloudformation as cfn,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    core
)

from common.var import *
import yaml

PARAMETER_FILE = PARAMETER.VPC
default_account = ACCOUNT().DEV_EVENT

# print(account_name)
# bucket_name = self.node.try_get_context("bucket_name")
# UPLOAD_BUCKET = BUCKET.UPLOADS3

# rule1 = Account1.Rule1
# rule2 = Account2.Rule1

# method_list = [func for func in dir(Account1) if callable(getattr(Account1, func)) and not func.startswith("__")]
# method_list = ['Account2.'+ func for func in dir(Account2) if not func.startswith("__")]
# method_list = [func for func in dir(Account2) if not func.startswith("__")]

# print(method_list)

# test = Account2.Rule1
# print(test)

# for x in method_list:
#     # mod = __import__(x, fromlist=[x])
#     cls = getattr(x, Account2)(class_args)
#     print(cls)


# print(mod)

# print(Account1().get_list())

# for index, sg in enumerate(rule1):
#     print(index, '', sg)

class SecurityGroupStacksets(core.Stack):

    def setTag(self, valueName, **kwargs):
        tagName = core.Token.as_any({
            "Key": "Name",
            "Value": valueName
        })
        tagArray = [tagName]

        for tKey, tValue in kwargs.items():
            tagArray.append(core.Token.as_any({
                "Key": tKey,
                "Value": tValue
            })
            )
        return tagArray

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ##############
        # parameters
        ##############

        with open(PARAMETER_FILE, 'r') as stream:
            try:
                params = yaml.safe_load(stream)
                # for item, doc in params.items():
                #     print(item, ":", doc)

            except yaml.YAMLError as e:
                print(e)

        params_map = {}
        for item, doc in params.items():
            if "AllowedValues" in doc:
                param = core.CfnParameter(self,
                                          id=item,
                                          type=doc["Type"],
                                          default=doc["Default"],
                                          description=doc["Description"],
                                          allowed_values=doc.get("AllowedValues")
                                          )
            else:
                param = core.CfnParameter(self,
                                          id=item,
                                          type=doc["Type"],
                                          default=doc["Default"],
                                          description=doc["Description"]
                                          )
            params_map[item] = param

        # vpcId = params_map["vpcId"]
        # # sharedAccountId = params_map["ShareToAccountId"]
        # envName = params_map["EnvironmentName"]
        # appName = params_map["ApplicationName"]
        
        # Get latest version or specified version of plain string attribute
        vpcId = ssm.StringParameter.value_for_string_parameter(self, "vpcId")
        envName = ssm.StringParameter.value_for_string_parameter(self, "envName")
        appName = ssm.StringParameter.value_for_string_parameter(self, "appName")
        if self.node.try_get_context("account_name") != None:
            account_name = self.node.try_get_context("account_name")
        else:
            account_name = default_account

        ##############
        # Resources
        ##############

        #### additional Security Group
        # web_sg = ec2.CfnSecurityGroup(
        #     self,
        #     'DefaultWebSecurityGroup',
        #     group_name=envName.value_as_string + '-' + appName.value_as_string + '-Default-Web',
        #     group_description=envName.value_as_string + '-' + appName.value_as_string + '-Default-Web',
        #     vpc_id=vpcId.value_as_string
        # )

        type_list = ['web', 'db', 'public']

        for t_list in type_list:
            service_sg = self.securitygroup_func(f'Default{t_list}SecurityGroup', 
                                    envName + '-' + appName + f'-Default-{t_list}',
                                    envName + '-' + appName + f'-Default-{t_list}',
                                    vpcId
                                    )
            ingress_security_group_ids = SGRULE().get_list_ingress(account_name, t_list)
            egress_security_group_ids = SGRULE().get_list_egress(account_name, t_list)
            # print(ingress_security_group_ids, t_list)
            # print(egress_security_group_ids, t_list)
            for index, sg in enumerate(ingress_security_group_ids):
                self.securitygroup_ingress_func(f"Default{t_list}SecurityGroupIngress{index}",
                                    service_sg.ref,
                                    sg[0],
                                    sg[1],
                                    sg[2],
                                    sg[3]
                                    )

            for index, sg in enumerate(egress_security_group_ids):
                self.securitygroup_egress_func(f"Default{t_list}SecurityGroupEgress{index}",
                                    service_sg.ref,
                                    sg[0],
                                    sg[1],
                                    sg[2],
                                    sg[3]
                                    )                                    

    def securitygroup_ingress_func(self, key, groupId, in_proto, f_port, t_port, ip):
        return ec2.CfnSecurityGroupIngress(self,
                                        id=key,
                                        group_id=groupId,
                                        ip_protocol=in_proto,
                                        from_port=f_port,
                                        to_port=t_port,
                                        cidr_ip=ip
                                        )

    def securitygroup_egress_func(self, key, groupId, in_proto, f_port, t_port, ip):
        return ec2.CfnSecurityGroupEgress(self,
                                        id=key,
                                        group_id=groupId,
                                        ip_protocol=in_proto,
                                        from_port=f_port,
                                        to_port=t_port,
                                        cidr_ip=ip
                                        )

    def securitygroup_func(self, key, groupname, groupdesc, vpcid):
        return ec2.CfnSecurityGroup(self,
                                    key,
                                    group_name=groupname,
                                    group_description=groupdesc,
                                    vpc_id=vpcid
        )

        # sgDefaultSubnet = ec2.CfnSecurityGroup(self,
        #                                        id="VPCEPrivateSubnetSecurityGroup",
        #                                        vpc_id=vpcId.value_as_string,
        #                                        group_description="Allow VPCEndpoints - Interfaces",
        #                                        security_group_ingress=[
        #                                            core.Token.as_any(
        #                                                {
        #                                                    "ipProtocol": "icmp",
        #                                                    "fromPort": -1,
        #                                                    "toPort": -1,
        #                                                    "cidrIp": "0.0.0.0/0"
        #                                                }),
        #                                            core.Token.as_any(
        #                                                {
        #                                                    "ipProtocol": "tcp",
        #                                                    "fromPort": 22,
        #                                                    "toPort": 22,
        #                                                    "cidrIp": "10.192.0.0/24"
        #                                                }),
        #                                            core.Token.as_any(
        #                                                {
        #                                                    "ipProtocol": "tcp",
        #                                                    "fromPort": 80,
        #                                                    "toPort": 80,
        #                                                    "cidrIp": "100.64.0.0/17"
        #                                                }),
        #                                            core.Token.as_any(
        #                                                {
        #                                                    "ipProtocol": "tcp",
        #                                                    "fromPort": 443,
        #                                                    "toPort": 443,
        #                                                    "cidrIp": "100.64.0.0/17"
        #                                                }),
        #                                            core.Token.as_any(
        #                                                {
        #                                                    "ipProtocol": "tcp",
        #                                                    "fromPort": 8080,
        #                                                    "toPort": 8080,
        #                                                    "cidrIp": "100.64.0.0/17"
        #                                                })
        #                                        ],
        #                                        security_group_egress=[
        #                                            core.Token.as_any(
        #                                                {
        #                                                    "ipProtocol": "-1",
        #                                                    "fromPort": -1,
        #                                                    "toPort": -1,
        #                                                    "cidrIp": "0.0.0.0/0"
        #                                                }),
        #                                            core.Token.as_any(
        #                                                {
        #                                                    "ipProtocol": "icmp",
        #                                                    "fromPort": -1,
        #                                                    "toPort": -1,
        #                                                    "cidrIp": "0.0.0.0/0"
        #                                                })

        #                                        ]
        #                                        )

        # addTag = {"i11::target-account-id": sharedAccountId.value_as_string}
        # sgDefaultSubnet.add_property_override("Tags", self.setTag(
        #     "SG-DEFAULT-" + appName.value_as_string + "-" + envName.value_as_string,
        #     **addTag
        # ))

        # app_lb_sg = ec2.CfnSecurityGroup(
        #     self,
        #     id='SharedApplicationLBSecurityGroup',
        #     group_description='Shared ALB Security Group',
        #     vpc_id=vpc_id,
        #     security_group_egress=[{
        #         'ipProtocol': 'tcp',
        #         'fromPort': application_port,
        #         'toPort': application_port,
        #         'destinationSecurityGroupId': app_sg.ref
        #     }]
        # )
        # app_sg_ingress = ec2.CfnSecurityGroupIngress(
        #     self,
        #     id='SharedApplicationSecurityGroupIngress',
        #     group_id=app_sg.ref,
        #     # source_security_group_id=app_lb_sg.ref,
        #     ip_protocol='tcp',
        #     from_port=application_port,
        #     to_port=application_port
        # )

    # def securitygroup_func(self, key, groupId, in_proto, f_port, t_port, ip):
    #     return ec2.CfnSecurityGroupIngress(self,
    #                                 # id="VPCEPrivateSubnetSecurityGroup",
    #                                 id=key,
    #                                 group_id=groupId,
    #                                 # vpc_id=vpc_id,
    #                                 # group_description="Allow VPCEndpoints - Interfaces",
    #                                 # group_description=desc
    #                                 ip_protocol=in_proto,
    #                                 from_port=f_port,
    #                                 to_port=t_port,
    #                                 cidr_ip=ip
                                    # security_group_ingress=[
                                    #     core.Token.as_any(
                                    #         {
                                    #             "ipProtocol": "icmp",
                                    #             "fromPort": -1,
                                    #             "toPort": -1,
                                    #             "cidrIp": "0.0.0.0/0"
                                    #         })]
                                    # security_group_egress=[
                                    #     core.Token.as_any(
                                    #         {
                                    #             "ipProtocol": "-1",
                                    #             "fromPort": -1,
                                    #             "toPort": -1,
                                    #             "cidrIp": "0.0.0.0/0"
                                    #         })]
                                    # )
