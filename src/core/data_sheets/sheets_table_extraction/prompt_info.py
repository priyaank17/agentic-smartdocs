"""This module contains functions for updating prompt information."""

import os
import datetime
import pandas as pd
from py_unified_cloud_adapter import get_adapter
from py_unified_cloud_adapter.models.requests import GetSecretRequest
from py_unified_cloud_adapter.utils.errors import CloudAdapterException
from src.utils.s3_download_upload import read_csv_from_storage, put_csv_in_storage
from src.utils.log import prompt_logger


async def prompt_info(output_csv_filename, name_chain_str, cb_str, time_stamp_str):
    """Update prompt information and save to an S3 bucket."""
    bucket = os.getenv("BUCKET", "default-bucket-name")

    try:
        existing_prompt_info_data = await read_csv_from_storage(bucket, output_csv_filename)
    except CloudAdapterException:
        existing_prompt_info_data = pd.DataFrame(
            columns=["Prompt", "Token Count", "Time Stamp"]
        )
    prompt_info = pd.DataFrame(  # pylint: disable=redefined-outer-name
        {
            "Prompt": [name_chain_str],
            "Token Count": [cb_str],
            "Time Stamp": [time_stamp_str],
        }
    )
    prompt_info_data = pd.concat(
        [existing_prompt_info_data, prompt_info], ignore_index=True
    )
    await put_csv_in_storage(
        data_df=prompt_info_data, bucket=bucket, destination=output_csv_filename
    )


async def update_prompt_information(
    prompt_template_name, cb_response, prompt_token_path
):
    """Update prompt information and save to an S3 bucket."""
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_stamp_str = str(time_stamp)
    name_chain_str = str(prompt_template_name)
    cb_str = str(cb_response)
    prompt_logger.info(
        f"The number of tokens that our prompt is using is... \n {cb_response}"
    )
    output_csv_filename = f"{prompt_token_path}/prompt_tokens.csv"
    await prompt_info(
        output_csv_filename,
        name_chain_str,
        cb_str,
        time_stamp_str
    )


async def get_openai_secret_key(secret_name="open_api_key"):
    """Get OpenAI secret key from AWS Secrets Manager."""
    client = get_adapter().secrets()

    try:
        get_secret_value_response = await client.get_secret(
            GetSecretRequest(secret_name=secret_name)
        )
    except CloudAdapterException as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    return secret
