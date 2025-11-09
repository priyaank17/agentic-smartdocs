"""This module contains functions to download and upload files from and to s3 bucket"""

from io import StringIO, BytesIO
import json
import pandas as pd
from py_unified_cloud_adapter import (  # type: ignore
    get_adapter,
    GetFileRequest,
    PutFileRequest,
    GetFileInfoRequest,
    DownloadFileRequest
)
from py_unified_cloud_adapter.utils.errors import CloudAdapterException  # type: ignore
from src.utils.log import logger

cloud_storage = get_adapter().storage()
local_storage = get_adapter("local").storage()


async def load_into_memory(bucket, path):
    """Returns byte data from storage"""
    if bucket:
        obj = await cloud_storage.get_file(GetFileRequest(bucket=bucket, path=path))
    else:
        obj = await local_storage.get_file(GetFileRequest(bucket="./", path=path))
    data = obj.data.data

    return data


async def put_object_in_storage(bucket, destination, data):
    """Uploads byte data to storage"""
    if bucket:
        await cloud_storage.put_file(
            PutFileRequest(bucket=bucket, path=destination, data=data)
        )
    else:
        await local_storage.put_file(
            PutFileRequest(bucket="./", path=destination, data=data)
        )


async def download_storage_file(bucket, file_path, local_destination):
    """Downloads file from storage"""
    await cloud_storage.download_file(
        DownloadFileRequest(
            bucket=bucket,
            source_path=file_path,
            destination_path=local_destination
        )
    )


async def put_csv_in_storage(data_df, bucket, destination):
    """Uploads csv data to storage"""
    csv_buffer = StringIO()
    data_df.to_csv(csv_buffer)
    await cloud_storage.put_file(
        PutFileRequest(bucket=bucket, path=destination, data=csv_buffer.getvalue())
    )


async def upload_csv_data(output_csv, op_bucket, op_path):
    """Uploads csv data to storage"""
    await put_csv_in_storage(data_df=output_csv, bucket=op_bucket, destination=op_path)


async def read_csv_from_storage(bucket, path):
    """Reads csv data from storage"""
    obj = await cloud_storage.get_file(GetFileRequest(bucket=bucket, path=path))

    # Create BytesIO object from the binary data
    csv_data = BytesIO(obj.data.data)

    # Read CSV using pandas
    initial_df = pd.read_csv(csv_data)
    return initial_df


async def file_exists_in_storage(bucket, path):
    """Checks if a file exists in storage"""
    try:
        await cloud_storage.get_file_info(
            GetFileInfoRequest(bucket=bucket, path=path)
        )
        return True
    except CloudAdapterException as e:
        if e.code == "404":
            return False
        raise


async def read_txt_from_storage(bucket, path):
    """Reads txt data from storage"""
    obj = await cloud_storage.get_file(GetFileRequest(bucket=bucket, path=path))
    contents = obj.data.data
    return contents


def list_objects_in_storage(bucket, path):
    """List files in s3"""
    file_list = []
    for obj in bucket.objects.filter(Prefix=path):
        file_list.append(obj.key)

    return file_list


async def load_json_from_storage(bucket, path):
    """Loads json data from storage"""
    if bucket:
        obj = await cloud_storage.get_file(GetFileRequest(bucket=bucket, path=path))
    else:
        obj = await local_storage.get_file(GetFileRequest(bucket=bucket, path=path))
    json_string = obj.data.data
    json_data = json.loads(json_string)
    return json_data


async def save_json_to_storage(bucket_name, key, data):
    """Saves JSON data to storage."""
    json_string = json.dumps(data)
    await cloud_storage.put_file(PutFileRequest(bucket=bucket_name, path=key, data=json_string))


async def check_file_in_storage(bucket, key):
    """Checks if file exists in S3 / Azure Blob"""
    try:
        output = await cloud_storage.get_file_info(GetFileInfoRequest(bucket=bucket, path=key))

        if not output or not output.success:
            logger.error(f"Failed to retrieve file info: {key}")
            return False

        if not output.data or not getattr(output.data, "success", False):
            logger.error(
                f"File does not exist or failed on provider side: {key}"
            )
            return False

        return True
    except CloudAdapterException as e:
        logger.error(f"[EXCEPTION] CloudAdapterException while checking file: {e}")
        return False


async def save_df_to_storage(bucket, csv_path, df):
    """Save the DataFrame to a storage as a CSV file."""
    # Convert the DataFrame to CSV format in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    await cloud_storage.put_file(
        PutFileRequest(bucket=bucket, path=csv_path, data=csv_buffer.getvalue())
    )
