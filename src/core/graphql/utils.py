"""This module contains utility functions"""

import json
import os
import requests
from src.utils.log import logger
from src.graphql.operations import (
    GET_PLANT_GRAPH_QL,
    GET_DOCUMENT_GRAPH_QL_STATUS,
    CREATE_GRAPH_QL_DATABASE,
    UPDATE_PLANT_GRAPH_QL,
    UPDATE_GRAPH_QL_DATABASE,
    UPDATE_DOCUMENT,
)
from src.utils.token import get_token

API_URL = os.getenv("APPSYNC_ENDPOINT")
REGION = os.getenv("REGION")
USER_GROUP = os.getenv("USER_GROUP")
ADMIN_GROUP = os.getenv("ADMIN_GROUP")
MEMBER_ID = os.getenv("MEMBER_ID")


def call_graph_ql(query, operation_name, operation_type, variables):
    """call graphql"""
    app_sync_url = API_URL
    # Create request
    token = get_token()
    res = requests.post(
        app_sync_url,
        data=json.dumps(
            {
                "query": query,
                "operation_name": operation_name,
                "operation_type": operation_type,
                "variables": variables,
            }
        ),
        headers={"Authorization": token, "Content-Type": "application/json"},
        timeout=10
    )
    res = res.json()
    logger.info(f"GraphQL response: {res}")

    return res


async def get_graph_ql_status(graph_id):
    """This function is used to get GraphQL status"""
    if not os.getenv("LOCAL", "false") == "true":
        logger.info("INIT: Getting GraphQL status")
        try:
            result = call_graph_ql(
                GET_PLANT_GRAPH_QL, "GET_PLANT_GRAPH_QL", "query", {"id": graph_id}
            )
            graph_ql_status = result["data"]["getPlant"]["graphDatabase"]
            if not graph_ql_status:
                step_status = call_graph_ql(
                    CREATE_GRAPH_QL_DATABASE,
                    "CREATE_GRAPH_QL_DATABASE",
                    "mutation",
                    {
                        "input": {
                            "UserGroup": USER_GROUP,
                            "AdminGroup": ADMIN_GROUP,
                            "createdBy": MEMBER_ID,
                            "status": "AVAILABLE",
                        },
                        "id": graph_id
                    },
                )
                status = step_status["data"]["createGraphDatabase"]["status"]
                graph_database_id = step_status["data"]["createGraphDatabase"]["id"]
                call_graph_ql(
                    UPDATE_PLANT_GRAPH_QL,
                    "UPDATE_PLANT_GRAPH_QL",
                    "mutation",
                    {"input": {"id": graph_id, "graphDatabaseID": graph_database_id}},
                )
            else:
                status = graph_ql_status
            final_status = {"success": True, "status": status}
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"Getting GraphQL status Failed: {str(e)}")
            final_status = {"success": False, "error": str(e)}
        logger.info(f"Getting GraphQL status: {final_status}")
        logger.info("DONE: Getting GraphQL status")
        return final_status
    return {"success": True}


async def get_graph_ql_document_status(graph_id):
    """This function is used to get GraphQL status"""
    if not os.getenv("LOCAL", "false") == "true":
        logger.info("INIT: Getting GraphQL Document status")
        try:
            # Call the GraphQL API
            result = call_graph_ql(
                GET_DOCUMENT_GRAPH_QL_STATUS, "status", "query", {"id": graph_id}
            )
            # Correctly access the 'getDocument' key
            document_status = result["data"]["getDocument"]["status"]
            status = document_status
            final_status = {"success": True, "status": status}

        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"Getting GraphQL status Failed: {str(e)}")
            final_status = {"success": False, "error": str(e)}

        logger.info(f"Getting GraphQL status: {final_status}")
        logger.info("DONE: Getting GraphQL status")
        return final_status

    # Return a default response for local environment
    return {"success": True}


async def update_graph_ql_status(graph_id, status):
    """
    Updates the status of the graph database
    """
    if not os.getenv("LOCAL", "false") == "true":
        logger.info("INIT: Updating GraphQL status")
        try:
            step_status = call_graph_ql(
                GET_PLANT_GRAPH_QL, "GET_PLANT_GRAPH_QL", "query", {"id": graph_id}
            )
            if (
                "data" in step_status
                and "getPlant" in step_status["data"]
                and "graphDatabase" in step_status["data"]["getPlant"]
            ):
                graph_database_id = step_status["data"]["getPlant"]["graphDatabase"][
                    "id"
                ]
                result = call_graph_ql(
                    UPDATE_GRAPH_QL_DATABASE,
                    "UPDATE_GRAPH_QL_DATABASE",
                    "mutation",
                    {"input": {"status": status}, "id": graph_database_id}
                )
                if result["data"]["updateGraphDatabase"]["status"] == status:
                    final_status = {"success": True, "status": status}
                else:
                    final_status = {
                        "success": False,
                        "status": result["data"]["updateGraphDatabase"],
                    }
            else:
                final_status = {"success": False, "error": "No graph database ID found"}
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"Updating GraphQL status Failed: {str(e)}")
            final_status = {"success": False, "error": str(e)}
        logger.info(f"Updating GraphQL status: {final_status}")
        logger.info("DONE: Updating GraphQL status")
        return final_status
    return {"success": True}


async def update_document_status(document_id, status):
    """This function updates the status of the document in the database."""
    # logger.info("INIT: In update_document_status")
    if not os.getenv("LOCAL", "false") == "true":
        logger.info("INIT: Updating Document")
        try:
            call_graph_ql(
                UPDATE_DOCUMENT,
                "UpdateDocument",
                "mutation",
                {"input": {"id": document_id, "status": status}},
            )
            final_status = {"success": True, "status": status}
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"Updating Document Failed: {str(e)}")
            final_status = {"success": False, "error": str(e)}
        logger.info(f"Updating Document: {final_status}")
        logger.info("DONE: Updating Document")
        return final_status
    return {"success": True}


async def update_document_junior_status(document_id, status):
    """This function updates the junior status of the document in the database."""
    if not os.getenv("LOCAL", "false") == "true":
        logger.info("INIT: Updating juniorOutputStatus for Document")
        try:
            call_graph_ql(
                UPDATE_DOCUMENT,
                "UpdateDocument",
                "mutation",
                {"input": {"id": document_id, "juniorOutputStatus": status}},
            )
            final_status = {"success": True, "juniorOutputStatus": status}
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"Updating Document Failed: {str(e)}")
            final_status = {"success": False, "error": str(e)}
        logger.info(f"Updating Document: {final_status}")
        logger.info("DONE: Updating juniorOutputStatus for Document")
        return final_status
    return {"success": True}
