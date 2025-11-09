"""This module consists of functions for extracting process narrative data"""

import json
from src.utils.log import logger
from src.process_narrative_rag.connection_data_extraction.extract_narrative import (
    get_data,
)
from src.graphql.utils import update_document_status


async def handle_EXTRACT_PROCESS_NARRATIVE_RAG_DATA(
    params,
):  # pylint: disable=invalid-name
    """
    Extract Process Narrative Data"""
    try:
        bucket_name = params["bucket_name"]
        pdf_path = params["plant_id"] + "/documents/" + params["document_id"]
        pid_connections_json_path = (
            + params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/p&id_source_destination_connection.json"
        )
        if "model_name" in params:
            model_name = params["model_name"]
        else:
            model_name = "gpt-4o"
        adm_json_path = (
            params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".PROCESS_NARRATIVE.adm.json"
        )

        input_files_path = {
            "pdf_file_path": pdf_path,
            "pid_source_destination_connection_path": pid_connections_json_path,
            "bucket_name": bucket_name,
            "plant_id": params["plant_id"],
            "document_id": params["document_id"],
        }
        await get_data(input_files_path, model_name, adm_json_path)
        await update_document_status(params["document_id"], "GENERATED")
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "msg": "Extracted Process narrative using rag successfully",
                    "path": adm_json_path,
                }
            ),
        }

    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.error("Error in handle_EXTRACT_PROCESS_NARRATIVE_RAG_DATA: %s", str(e))
        await update_document_status(params["document_id"], "ERROR")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_EXTRACT_PROCESS_NARRATIVE_DATA: {str(e)}",
                }
            ),
        }
