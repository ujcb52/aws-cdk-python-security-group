#!/usr/bin/env python3

from aws_cdk import core

from stacks.security_group_stacks import SecurityGroupStacks
from stacksets.security_group_stacksets import SecurityGroupStacksets


app = core.App()

SecurityProp = app.node.try_get_context('security')
SecurityGroupStacks(app, "security-stacks", props=SecurityProp)
SecurityGroupStacksets(app, "security-stacksets", props=SecurityProp)

app.synth()
