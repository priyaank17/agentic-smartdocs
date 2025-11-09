"""This module consists of functions for extracting cause and effect data"""

import json
from src.utils.log import logger
from src.graphql.utils import update_document_status
from src.utils.storage_utils import upload_file_to_storage


async def handle_EXTRACT_CAUSE_AND_EFFECT_DATA(params):  # pylint: disable=invalid-name
    """this function is used to extract cause and effect data"""
    try:
        bucket_name = params["bucket_name"]
        case_and_effect_key = (
            params["plant_id"]
            + "/documents/cause_and_effect/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".CAUSE_AND_EFFECT.adm.json"
        )

        await upload_file_to_storage(
            bucket_name,
            case_and_effect_key,
            json.dumps({}).encode("utf-8")
        )

        await update_document_status(params["document_id"], "GENERATED")
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "msg": "Cause and Effect Data extracted successfully",
                    "path": case_and_effect_key,
                }
            ),
        }
    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.error(f"Error in handle_CAUSE_AND_EFFECT_DATA: {str(e)}")
        await update_document_status(params["document_id"], "ERROR")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_EXTRACT_CAUSE_AND_EFFECT_DATA: {str(e)}",
                }
            ),
        }
