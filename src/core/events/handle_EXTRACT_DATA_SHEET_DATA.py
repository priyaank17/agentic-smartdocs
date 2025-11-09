"""This module consists of functions for extracting data sheet data"""

import json
from src.utils.storage_utils import upload_file_to_storage
from src.utils.log import logger
from src.graphql.utils import update_document_status
from src.constants.Extractions import Extractions
from src.data_sheets.sheets_table_extraction.extract import get_data
from src.data_sheets.sheet_adm_generation.generate_adm import generate_adm


async def handle_EXTRACT_DATA_SHEET_DATA(params):  # pylint: disable=invalid-name
    """
    Extract Data Sheet Data"""
    try:
        logger.info("Extracting Data Sheet Data")
        bucket_name = params["bucket_name"]
        extract_type = params["extract_type"]
        plant_id = params["plant_id"]
        document_id = params["document_id"]
        path = f"{plant_id}/documents/data_sheet/{document_id}"
        input_data_path = f"{path}/input_data.json"
        data_sheet_key = (
            params["plant_id"]
            + "/documents/data_sheet/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".DATA_SHEET.adm.json"
        )
        if extract_type == Extractions.INITIAL_DATA_SHEET_EXTRACTION:
            logger.info(f"Extracting Data Sheet Data for {extract_type}")
            await upload_file_to_storage(
                bucket_name,
                data_sheet_key,
                json.dumps({}),
            )
        elif extract_type == Extractions.DATA_SHEET_TABLE_EXTRACTION:
            logger.info(f"Extracting Data Sheet Data for {extract_type}")
            await get_data(input_data_path, bucket_name)
        elif extract_type == Extractions.DATA_SHEET_GENERATE_ADM:
            logger.info(f"Extracting Data Sheet Data for {extract_type}")
            csv_files_path = f"{plant_id}/documents/data_sheet/{document_id}"
            await generate_adm(input_data_path, csv_files_path, bucket_name)
        else:
            await update_document_status(params["document_id"], "ERROR")
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "success": False,
                        "msg": f"Invalid extract_type: {extract_type}",
                    }
                ),
            }
        await update_document_status(params["document_id"], "GENERATED")
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "msg": f"Data Sheet Data extracted successfully for {extract_type}",
                    "path": data_sheet_key,
                }
            ),
        }
    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.error(f"Error in handle_DATA_SHEET_EXTRACTION: {str(e)}")
        await update_document_status(params["document_id"], "ERROR")
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_DATA_SHEET_EXTRACTION: {str(e)}",
                }
            ),
        }
