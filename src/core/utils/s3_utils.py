"""File for s3 utils"""

import json
import os
import boto3
from py_unified_cloud_adapter import get_adapter, PutFileRequest, GetFileRequest  # type: ignore
from py_unified_cloud_adapter.utils.errors import CloudAdapterException  # type: ignore
from src.utils.log import logger


CONFIG_FILE_PATH = "data/configs/config.json"


async def upload_object_to_s3(data, s3_path):
    """Upload object to s3"""
    s3_client = get_adapter().storage()
    response = await s3_client.put_file(
        PutFileRequest(bucket="your-bucket-name", data=data, path=s3_path)
    )
    logger.info(f"Uploaded object to s3 at {s3_path}")
    return response


def save_file_to_local(file_path, db_ready_adm):
    """Save file to local"""
    logger.info("INIT: Saving file to local")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)
    local_path_db_ready = os.path.join(
        config["adms_db_ready_folder_path"], os.path.basename(file_path)
    )
    with open(local_path_db_ready, "w", encoding="utf-8") as file:
        json.dump(db_ready_adm, file)
    logger.info(f"DONE: Saving File at: {local_path_db_ready}")
    return local_path_db_ready


def save_index_to_s3(
    report_name, report_file_prefix, exportable_record_sets, s3_folder_path
):
    """Save index to s3"""
    logger.info("INIT: save_index_to_s3")
    upload_object_to_s3(
        json.dumps(exportable_record_sets),
        os.path.join(s3_folder_path, report_file_prefix),
    )
    for record in exportable_record_sets:
        upload_object_to_s3(
            json.dumps(record["data"]), os.path.join(s3_folder_path, record["name"])
        )
    logger.info(f"Report ADM: {report_name} written to S3 successfully.")
    logger.info("DONE: save_index_to_s3")


def save_adm_to_s3(drawing_number, adm_string, s3_folder_path):
    """Save adm to s3"""
    logger.info("INIT: save_adm_to_s3")
    file_path = f"{s3_folder_path}/adms/{drawing_number}.json"
    upload_object_to_s3(json.dumps(adm_string), file_path)
    logger.info(f"Report: {drawing_number} written to S3 successfully.")
    logger.info("DONE: save_adm_to_s3")


def read_file_from_s3(bucket_name, file_path):
    """Read file from s3"""
    logger.info(
        {
            "step": 2,
            "message": "Starting Reading file content",
            "bucket_name": bucket_name,
            "file_path": file_path,
            "region": boto3.session.Session().region_name,
        }
    )

    try:
        s3 = get_adapter().storage()
        response = s3.get_file(GetFileRequest(bucket=bucket_name, path=file_path))
        logger.info(
            {
                "step": 3,
                "message": "s3 params",
                "params": {"Bucket": bucket_name, "Key": file_path},
            }
        )

        body = response.data.data
        data = json.loads(body)

        logger.info({"step": 4, "message": "Successfully Read File"})
        return {"success": True, "data": data}
    except CloudAdapterException as error:
        logger.error({"step": 4, "location": "read_file_from_s3", "error": str(error)})
        return {"success": False, "error": str(error)}
