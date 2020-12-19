import json
import pytest

from aws_cdk import core
from python-security-group.python_security_group_stack import PythonSecurityGroupStack


def get_template():
    app = core.App()
    PythonSecurityGroupStack(app, "python-security-group")
    return json.dumps(app.synth().get_stack("python-security-group").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
