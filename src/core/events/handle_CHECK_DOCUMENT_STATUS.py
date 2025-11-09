"""This module is responsible for checking the status of the long-running process"""

import json
from src.graphql.utils import get_graph_ql_document_status
from src.utils.log import logger


async def handle_CHECK_DOCUMENT_STATUS(event):  # pylint: disable=invalid-name
    """Check the status of the long-running triggered process"""
    logger.info("checking status")
    document_id = event["document_id"]

    status_response = await get_graph_ql_document_status(document_id)
    if status_response.get("status") == "GENERATED":
        logger.info("Status: %s", status_response.get("status"))
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "status": status_response["status"]}),
        }
    if status_response.get("status") == "IN_PROGRESS":
        logger.info("Status: %s", status_response.get("status"))
        return {
            "statusCode": 202,
            "body": json.dumps({"success": True, "status": status_response["status"]}),
        }
    if status_response.get("status") == "NOT GENERATED":
        logger.info("Status: %s", status_response.get("status"))
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "Status": False,
                    "msg": "Extraction Not Started or Updated.",
                    "status": status_response["status"],
                }
            ),
        }
    logger.info("Status: %s", status_response.get("status"))
    return {
        "statusCode": 500,
        "body": json.dumps(
            {
                "success": False,
                "msg": "Failed to retrieve status",
                "error": status_response.get("error", "Unknown error"),
            }
        ),
    }
