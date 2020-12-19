from aws_cdk import (
    core
)
import yaml
from common.cdk_common import *
from common.var import *

#ACCOUNT_ID = ACCOUNT.SHARED
STACKSET_URL = "https://" + BUCKET.CREATED + ".s3.ap-northeast-2.amazonaws.com/securitygroup/stacksets/cfn/"
# STACKSET_NAME = "subnet-stackset"

PARAMETER_FILE = PARAMETER.VPC
ACCOUNT_LIST = ACCOUNT().get_account_list()

class SecurityGroupStacks(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        core.CfnMapping(
            self,
            id="LambdaFunction",
            mapping={
                "Logging": {
                    "Level": "info"
                }
            }
        )

        # accountId = cfnParam(core, self, "AccountId", ACCOUNT.SHARED, "Shared Account Number")
        region = cfnParam(core, self, "Region", REGION.SEOUL, "Target region for VPC")
        stacksetName = cfnParam(core, self, "StackSetName", "SecurityGroup-Stacks", "Stack Set Name for Shared Services Subnet")

        ### through parameters
        params_list, params_map, paramObj = getStackParams(core, self, PARAMETER_FILE)

        # # core.ITemplateOptions.metadata = {
        # self.template_options.metadata = {
        #     'ParameterGroups': [
        #         {
        #             'Label': {'default': 'Target Account Information'},
        #             'Parameters': [accountId.logical_id]
        #         },
        #         {
        #             'Label': {'default': 'Region to deploy the VPC'},
        #             'Parameters': [region.logical_id]
        #         },
        #         {
        #             'Label': {'default': 'VPC Details'},
        #             'Parameters': params_list
        #         }
        #     ]

        # }
        for account_id in ACCOUNT_LIST:        
            core.CustomResource(
                self,
                "SecurityGroupStackSet-" + account_id,
                resource_type="Custom::StackInstance",
                properties={
                    # "StackSetName": stacksetName.value_as_string + "-" + account_id + paramObj["EnvironmentName"].value_as_string + "-" +
                    #                 paramObj["ApplicationName"].value_as_string,
                    "StackSetName": stacksetName.value_as_string + "-" + account_id,                    
                    "TemplateURL": STACKSET_URL + account_id + "/security-group-stacksets.yaml",
                    # "AccountList": [accountId.value_as_string],
                    "AccountList": [account_id],
                    "RegionList": [region.value_as_string],
                    "Parameters": params_map,
                    "Capabilities": "CAPABILITY_NAMED_IAM",
                    "ServiceToken": "arn:aws:lambda:ap-northeast-2:" + ACCOUNT.MASTER + ":function:LandingZone"
                },
                service_token="arn:aws:lambda:ap-northeast-2:" + ACCOUNT.MASTER + ":function:LandingZone"
            )
