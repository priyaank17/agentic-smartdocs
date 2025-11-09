"""Keys.

This file would provide functionality to get the secret keys from
AWS Secrets Manager

# If you need more information about configurations or implementing
# the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/
"""

import base64
import os
import json
from py_unified_cloud_adapter import get_adapter
from py_unified_cloud_adapter.models.requests import GetSecretRequest
from py_unified_cloud_adapter.utils.errors import CloudAdapterException
from dotenv import load_dotenv
from .log import logger

load_dotenv()

GOOGLE_SERVICE_ACCOUNT_CONFIG = "GOOGLE_SERVICE_ACCOUNT_CONFIG"
AUTH_TOKEN = "AUTH_TOKEN"
JWT_SECRET_KEY = "JWT_SECRET_KEY"


SECRET_KEYS = None


async def get_secret_from_aws():
    """Get Secret from AWS."""
    logger.info("Loading Secrets from AWS Secrets Manager")
    secret_name = os.getenv("ASM_SECRET_NAME")
    # region_name = os.getenv("AWS_DEFAULT_REGION")

    client = get_adapter().secrets()

    # In this sample we only handle the specific exceptions for
    # the 'GetSecretValue' API.
    # See the following link for the 'GetSecretValue' API:
    # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    default_secret = {
        JWT_SECRET_KEY: "",
        AUTH_TOKEN: "",
        GOOGLE_SERVICE_ACCOUNT_CONFIG: "{}",
    }
    get_secret_value_response = {}
    try:
        get_secret_value_response = await client.get_secret(
            GetSecretRequest(
                secret_name=secret_name
            )
        )
    except CloudAdapterException as e:
        error_code = str(e)
        error_messages = {
            "DecryptionFailureException": (
                "Secrets Manager can't decrypt the protected secret text "
                "using the provided KMS key."
            ),
            "InternalServiceErrorException": "An error occurred on the server side.",
            "InvalidParameterException": (
                "You provided an invalid value for a parameter."
            ),
            "InvalidRequestException": (
                "You provided a parameter value that is not valid for the "
                "current state of the resource."
            ),
            "ResourceNotFoundException": (
                "We can't find the resource that you asked for."
            ),
        }
        logger.error(
            f"""Error while getting Secret:
            {error_code} - {error_messages.get(error_code, 'Unknown error')} {str(e)}"""
        )
        return default_secret
    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary,
    # one of these fields will be populated.

    secret = '{"JWT_SECRET_KEY": "", "AUTH_TOKEN": ""}'
    logger.info("Obtained Secrets")
    logger.info(get_secret_value_response)
    if "SecretString" in get_secret_value_response:
        secret = get_secret_value_response["SecretString"]

    else:  # Find out how to use decoded_binary_secret
        decoded_binary_secret = base64.b64decode(
            get_secret_value_response["SecretBinary"].decode("utf-8")
        )
        secret = decoded_binary_secret
    secret_keys = json.loads(secret)
    logger.info("Successfully fetched ArtisanSecret")
    return secret_keys


def get_secret_from_env():
    """Get Secret from Env."""
    logger.info("Loading Secrets from Environment")
    return {
        JWT_SECRET_KEY: os.getenv(JWT_SECRET_KEY),
        AUTH_TOKEN: os.getenv(AUTH_TOKEN),
        GOOGLE_SERVICE_ACCOUNT_CONFIG: os.getenv(GOOGLE_SERVICE_ACCOUNT_CONFIG),
    }


async def load_secret_keys():
    """Load Secret Keys."""
    global SECRET_KEYS  # pylint: disable=global-statement

    if SECRET_KEYS is not None:
        return SECRET_KEYS

    if "DO_NOT_USE_ASM" in os.environ:
        SECRET_KEYS = get_secret_from_env()
        logger.info("Loading Secrets from Environment Completed..")
    else:
        SECRET_KEYS = await get_secret_from_aws()
        logger.info("Loading Secrets from AWS Environment Completed..")

    return SECRET_KEYS


async def get_jwt():
    """Get JWT."""
    await load_secret_keys()
    return SECRET_KEYS[JWT_SECRET_KEY]


async def get_auth_token():
    """Get Auth Token."""
    await load_secret_keys()
    return SECRET_KEYS[AUTH_TOKEN]


async def get_google_service_config():
    """Get Google Service Config."""
    await load_secret_keys()
    return SECRET_KEYS[GOOGLE_SERVICE_ACCOUNT_CONFIG]
