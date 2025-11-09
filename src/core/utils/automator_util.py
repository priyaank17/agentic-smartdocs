"""Utility functions for automator."""

import datetime
from botocore.config import Config
import boto3
from py_unified_cloud_adapter import get_adapter


def setup_aws_clients():
    """Setup AWS clients."""
    my_config = Config(region_name="us-west-2")
    storage = get_adapter().secrets()
    step_fn = boto3.client("stepfunctions", config=my_config)
    lambda_client = boto3.client("lambda", config=my_config)
    return storage, step_fn, lambda_client


def invoke_lambda(lambda_client, function_name, payload):
    """Invoke lambda function."""
    response = lambda_client.invoke(
        FunctionName=function_name, InvocationType="RequestResponse", Payload=payload
    )
    return response


def get_current_time():
    """Get current time."""
    return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
