"""
Storage utils for reading and writing files to local and cloud storage.
"""

import json
from py_unified_cloud_adapter import (  # type: ignore
    GetFileRequest,
    PutFileRequest,
    GetFileInfoRequest,
    ListFilesRequest,
    get_adapter,
)
from py_unified_cloud_adapter.utils.errors import CloudAdapterException  # type: ignore
from src.utils.log import logger

storage = get_adapter().storage()


async def read_local_file_via_adapter(local_storage, path):
    """
    Reads a file from local storage using py_unified_cloud_adapter.

    :param local_storage: Local storage adapter instance
    :param path: Path of the file to be read
    :return: Parsed JSON content of the file
    """
    logger.info(f"Reading file from local storage: {path}")
    file_request = await local_storage.get_file(GetFileRequest(bucket="./", path=path))

    if not file_request.success and not file_request.data.success:
        raise FileNotFoundError(f"Failed to read file from local storage: {path}")

    return json.loads(file_request.data.data)


async def write_local_file_via_adapter(local_storage, path, data):
    """
    Writes a file to local storage using py_unified_cloud_adapter.

    :param local_storage: Local storage adapter instance
    :param path: Path where the file will be written
    :param data: Data to be written (as bytes)
    :return: None
    """
    logger.info(f"Writing file to local storage: {path}")
    file_request = await local_storage.put_file(
        PutFileRequest(bucket="./", path=path, data=data)
    )
    if not file_request.success and not file_request.data.success:
        raise IOError(f"Failed to write file to local storage: {path}")

    return file_request


async def upload_file_to_storage(bucket, path, data):
    """
    Uploads a file to cloud storage using py_unified_cloud_adapter.

    :param bucket: Cloud storage bucket name
    :param path: Path where the file will be uploaded
    :param data: Data to be uploaded (as bytes)
    :return: None
    """
    logger.info(f"Uploading file to cloud storage: {path}")
    if bucket:
        put_request = await storage.put_file(
            PutFileRequest(bucket=bucket, path=path, data=data)
        )
    else:
        put_request = await storage.put_file(
            PutFileRequest(bucket="./", path=path, data=data)
        )

    if not put_request.success and not put_request.data.success:
        raise IOError(f"Failed to upload file to storage: {path}")
    logger.info(f"Uploaded file to storage: {path}")


async def fetch_cloud_file_via_adapter(cloud_storage, bucket, path):
    """
    Fetches a file from cloud storage using py_unified_cloud_adapter.

    :param cloud_storage: Cloud storage adapter instance
    :param bucket: Cloud storage bucket name
    :param path: Path of the file to be fetched
    :return: Parsed JSON content of the file
    """
    logger.info(f"Fetching file from cloud storage: {path}")
    file_request = await cloud_storage.get_file(
        GetFileRequest(bucket=bucket, path=path)
    )
    # print(file_request)

    if not file_request.success and not file_request.data.success:
        raise FileNotFoundError(f"Failed to fetch file from cloud storage: {path}")
    return json.loads(file_request.data.data)


async def fetch_file_via_adapter(bucket, path):
    """
    Fetches a file from cloud storage using py_unified_cloud_adapter.

    :param bucket: Cloud storage bucket name
    :param path: Path of the file to be fetched
    :return: Parsed JSON content of the file
    """
    logger.info(f"Fetching file from storage: {path}")
    if bucket:
        file_request = await storage.get_file(GetFileRequest(bucket=bucket, path=path))
    else:
        file_request = await storage.get_file(GetFileRequest(bucket="./", path=path))

    if not file_request.success and not file_request.data.success:
        raise FileNotFoundError(f"Failed to fetch file from cloud storage: {path}")
    return json.loads(file_request.data.data)


async def fetch_cloud_pdf_via_adapter(bucket, path):
    """
    Fetches a file from cloud storage using py_unified_cloud_adapter.

    :param cloud_storage: Cloud storage adapter instance
    :param bucket: Cloud storage bucket name
    :param path: Path of the file to be fetched
    :return: File content in appropriate format (JSON for .json files, bytes for binary files)
    :raises: ValueError if JSON parsing fails
    """
    logger.info(f"Fetching file from cloud storage: {path}")
    if bucket:
        file_request = await storage.get_file(GetFileRequest(bucket=bucket, path=path))
    else:
        file_request = await storage.get_file(GetFileRequest(bucket="./", path=path))

    if not file_request.success and not file_request.data.success:
        raise FileNotFoundError(f"Failed to fetch file from cloud storage: {path}")

    # Get the raw data
    raw_data = file_request.data.data

    # Check if it's a PDF file by looking at the magic bytes
    if isinstance(raw_data, bytes) and raw_data.startswith(b"%PDF"):
        logger.warning(f"Found PDF file at {path}")
        return file_request

    # Try to parse as JSON
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:  # pylint: disable=raise-missing-from
        logger.error(f"Failed to parse JSON from {path}")


async def upload_file_to_cloud_via_adapter(cloud_storage, bucket, path, data):
    """
    Uploads a file to cloud storage using py_unified_cloud_adapter.

    :param cloud_storage: Cloud storage adapter instance
    :param bucket: Cloud storage bucket name
    :param path: Path where the file will be uploaded
    :param data: Data to be uploaded (as bytes)
    :return: None
    """
    logger.info(f"Uploading file to cloud storage: {path}")
    # data_bytes = json.dumps(data).encode('utf-8')
    put_request = await cloud_storage.put_file(
        PutFileRequest(bucket=bucket, path=path, data=data)
    )

    if not put_request.success and not put_request.data.success:
        raise IOError(f"Failed to upload file to cloud storage: {path}")
    logger.info(f"Uploaded file to cloud storage: {path}")


async def get_cloud_image_info_via_adapter(cloud_storage, bucket, path):
    """
    Fetches image information from cloud storage using py_unified_cloud_adapter.

    :param cloud_storage: Cloud storage adapter instance
    :param bucket: Cloud storage bucket name
    :param path: Path of the image file to be fetched
    :return: Image information (size, format, etc.)
    """
    logger.info(f"Fetching image info from cloud storage: {path}")
    try:
        await cloud_storage.get_file_info(GetFileInfoRequest(bucket=bucket, path=path))
        return True
    except CloudAdapterException as e:
        if e.code == "404":
            return False
        raise


async def list_objects_in_storage(bucket, path):
    """
    Lists objects in cloud storage using py_unified_cloud_adapter.

    :param bucket: Cloud storage bucket name
    :param path: Path prefix for filtering objects
    :return: List of object keys
    """
    logger.info(f"Listing objects in cloud storage: {path}")
    response = await storage.list_files(
        ListFilesRequest(bucket=bucket, prefix=path)
    )
    return response.data
