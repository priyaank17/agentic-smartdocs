"""This module consists of functions for extracting data sheet data"""

import json
from src.utils.log import logger
from src.constants.Extractions import Extractions
from src.data_sheets.get_standard_details.get_standard_data_sheet_data import (
    get_asset_class,
    get_table_name,
)
from src.utils.storage_utils import upload_file_to_storage


async def handle_GET_DATA_SHEET_STANDARD_DETAILS(
    params,
):  # pylint: disable=invalid-name
    """
    Extract Data Sheet Data"""
    try:
        logger.info("Extracting Data Sheet Data")
        bucket_name = params["bucket_name"]
        extract_type = params["extract_type"]
        plant_id = params["plant_id"]
        path = f"{plant_id}/documents/data_sheet"
        size_limit = 6 * 1024 * 1024  # 6MB in bytes
        if extract_type == Extractions.DATA_SHEET_STANDARD_TABLE_NAME:
            logger.info(f"Get standard table name for {extract_type}")
            standard_table_name = get_table_name()
            if is_output_size_over_limit(standard_table_name, size_limit):
                tables_name_json = json.dumps(standard_table_name)
                return await handle_large_output(
                    tables_name_json, bucket_name, path, "standard_table_name.json"
                )
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "success": True,
                        "msg": f"Data Sheet Data extracted successfully for {extract_type}",
                        "data": standard_table_name,
                    }
                ),
            }
        if extract_type == Extractions.DATA_SHEET_STANDARD_ASSET_CLASS_NAME:
            logger.info(f"Get standard asset class name for {extract_type}")
            standard_asset_class = get_asset_class()
            if is_output_size_over_limit(standard_asset_class, size_limit):
                asset_class_json = json.dumps(standard_asset_class)
                return await handle_large_output(
                    asset_class_json, bucket_name, path, "standard_asset_class.json"
                )
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "success": True,
                        "msg": f"Data Sheet Data extracted successfully for {extract_type}",
                        "data": standard_asset_class,
                    }
                ),
            }
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"success": False, "msg": f"Invalid extract_type: {extract_type}"}
            ),
        }
    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.error(f"Error in handle_DATA_SHEET_EXTRACTION: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_DATA_SHEET_EXTRACTION: {str(e)}",
                }
            ),
        }


def is_output_size_over_limit(table_name, size_limit):
    """Check size of the table name"""
    my_string = " ".join(table_name)
    table_name_size_bytes = len(my_string.encode("utf-8"))
    if table_name_size_bytes > size_limit:
        return True
    return False


async def handle_large_output(data, bucket_name, path, file_name):
    """Handle large output"""

    logger.info("handle_large_output and save it in s3")
    data_json = json.dumps(data)
    await upload_file_to_storage(
        bucket_name,
        f"{path}/{file_name}",
        data_json.encode("utf-8"),
    )
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "success": True,
                "msg": f"Output size for {file_name.split('.')[0]} is over "
                f"the limit. Saved in S3 bucket",
                "path": f"{path}/{file_name}",
            }
        ),
    }
