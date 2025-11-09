"""
This module is responsible for handle_TRIGGERED_DATA_SHEET_DATA_ACTION event."""
import json
from py_unified_cloud_adapter.utils.errors import CloudAdapterException
import boto3
from src.utils.log import logger
from src.graphql.utils import update_document_status
lambda_client = boto3.client("lambda")


async def handle_TRIGGERED_DATA_SHEET_DATA_ACTION(params):  # pylint: disable=invalid-name
    """handle_TRIGGERED_DATA_SHEET_DATA_ACTION"""
    logger.info("INIT: handle_TRIGGERED_DATA_SHEET_DATA_ACTION")
    try:
        document_id = params["document_id"]

        await update_document_status(document_id, "IN_PROGRESS")
        params["action"] = "EXTRACT_DATA_SHEET_DATA"
        lambda_client.invoke(
            FunctionName="artisan-narrative-asset-association",
            InvocationType="Event",
            Payload=json.dumps(params)
        )
        logger.info("Request accepted, processing started.")
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "msg": "Request accepted, processing started.",
                "document_id": document_id
            })
        }
    except KeyError as e:
        logger.error("Missing key in parameters: %s", str(e))
        await update_document_status(params.get("document_id", "unknown"), "ERROR")
        return {
            "statusCode": 400,
            "body": json.dumps({
                "success": False,
                "msg": f"Missing key in parameters: {str(e)}"
            })
        }
    except CloudAdapterException as e:
        logger.error("Boto3 client error: %s", str(e))
        await update_document_status(params.get("document_id", "unknown"), "ERROR")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "msg": f"Boto3 client error: {str(e)}"
            })
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Unexpected error in handle_TRIGGERED_DATA_SHEET_DATA_ACTION: %s", str(e))
        await update_document_status(params.get("document_id", "unknown"), "ERROR")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "msg": f"Unexpected error in handle_TRIGGERED_DATA_SHEET_DATA_ACTION: {str(e)}"
            })
        }
