"""Get the OpenAI key from AWS Secrets Manager."""
import json
from py_unified_cloud_adapter import get_adapter
from py_unified_cloud_adapter.models.requests import GetSecretRequest
from py_unified_cloud_adapter.utils.errors import CloudAdapterException


async def get_secret(secret_name):
    """Get the secret from AWS Secrets Manager."""
    secret_name = "ArtisanSecrets_Dev"

    # Create a Secrets Manager client
    client = get_adapter().secrets()

    try:
        get_secret_value_response = await client.get_secret(
            GetSecretRequest(
                secret_name=secret_name
            )
        )
    except CloudAdapterException as e:
        raise e

    secret = json.loads(get_secret_value_response.data.secrets)
    return secret
