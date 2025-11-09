"""This module is responsible for handling the GET_LIST_OF_DOCUMENTS event."""

import os
import json
import boto3
import requests

from src.utils.log import logger
from src.events.utils import get_return_type
from src.graphql.utils import get_graph_ql_status, update_graph_ql_status
from src.constants import DatabaseStatus
from src.utils.token import get_token

dynamodb = boto3.resource("dynamodb")
appsync_client = boto3.client("appsync")
APPSYNC_ENDPOINT = os.getenv("APPSYNC_ENDPOINT")
GET_DOCUMENTS_QUERY = """
  query GetPlant($id: ID!, $nextToken: String) {
    getPlant(id: $id) {
      name
      documents(nextToken: $nextToken, limit: 1000) {
        items {
          id
          name
          inventoryTable {
            fileName
            id
            digitizationStatus
            titleBoxInfo {
              facilityAreaInfo {
                drawingName
                drawingNo
                drawingType
              }
            }
          }
          status
          type
        }
        nextToken
      }
    }
  }
"""


def _api_call(plant_id):

    if APPSYNC_ENDPOINT is None:
        logger.error("APPSYNC_ENDPOINT not found in .env")
        return {
            "success": False,
            "msg": "Error. APPSYNC_ENDPOINT not found in .env",
        }

    logger.info("Sending request to AppSync to check plantId")
    token = get_token()
    response = requests.post(
        url=APPSYNC_ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "Authorization": token
        },
        data=json.dumps({
            "query": GET_DOCUMENTS_QUERY,
            "variables": {"id": plant_id}
        }),
        timeout=10
    )
    response_data = response.json()
    if "errors" in response_data:
        logger.error("ERROR: Fetching the Documents list %s", response_data['errors'])
        raise ValueError(response_data["errors"])

    try:
        result = response_data["data"]["getPlant"]["documents"]["items"]
        document_types = [
            "DATA SHEET",
            "HMB",
            "PROCESS FLOW DIAGRAM",
            "PROCESS NARRATIVE",
            "CONTROL NARRATIVE",
            "CAUSE AND AFFECT",
            "GENERAL AGREEMENT",
        ]
        result = [
            doc
            for doc in result
            if doc["type"] in document_types and doc["status"] == "GENERATED"
        ]
        items = []
        for item in result:
            data = item
            doc_type = item["type"].replace(" ", "_").upper()
            if doc_type == "CONTROL_NARRATIVE":
                adm_path_inst = (
                    f"{plant_id}/documents/{doc_type}/{item['id']}/{item['id']}"
                    + f".{doc_type}.inst.adm.json"
                )
                adm_path_cl = (
                    f"{plant_id}/documents/{doc_type}/{item['id']}/{item['id']}"
                    + f".{doc_type}.cl.adm.json"
                )
                data["adm_path_inst"] = adm_path_inst
                data["adm_path_cl"] = adm_path_cl
            else:
                adm_path = (
                    f"{plant_id}/documents/{doc_type}/{item['id']}/{item['id']}"
                    + f".{doc_type}.adm.json"
                )
                data["adm_path"] = adm_path
            data["plant_id"] = plant_id
            items.append(data)

    except KeyError as err:
        logger.error("ERROR: Fetching the Documents list %s", err)
        items = None

    return items


async def handle_GET_LIST_OF_DOCUMENTS(is_api_event, payload):  # pylint: disable=invalid-name
    """handle_GET_LIST_OF_DOCUMENTS"""
    logger.info("INIT: handle_GET_LIST_OF_DOCUMENTS")
    plant_id = payload["plant_id"]
    step_status_graph_ql = await get_graph_ql_status(plant_id)
    if step_status_graph_ql["success"]:
        await update_graph_ql_status(plant_id, DatabaseStatus.GETTING_LIST_OF_DOCUMENTS)

    try:
        data = _api_call(plant_id)
        step_status_graph_ql = await get_graph_ql_status(plant_id)
        if step_status_graph_ql["success"]:
            await update_graph_ql_status(
                plant_id, DatabaseStatus.GETTING_LIST_OF_DOCUMENTS_SUCCESSFUL
            )
        step_status = {"success": True, "data": data}
    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.error("ERROR: handle_GET_LIST_OF_DOCUMENTS: %s", e)
        await update_graph_ql_status(
            plant_id, DatabaseStatus.GETTING_LIST_OF_DOCUMENTS_FAILED
        )
        step_status = {"success": False, "error": str(e)}

    logger.info("DONE: handle_GET_LIST_OF_DOCUMENTS")
    return get_return_type(is_api_event, step_status)
