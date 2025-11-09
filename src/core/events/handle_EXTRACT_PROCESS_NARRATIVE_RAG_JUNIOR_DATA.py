"""This module consists of functions for extracting process narrative data"""

import json
from src.utils.log import logger
# from src.process_narrative_rag_junior.connection_data_extraction.extract_narrative import (
#     get_data,
# )
from src.process_narrative_rag_junior.extract_stream_conditions.extract_narrative import (
    get_data,
)
from src.process_narrative_rag_junior.extract_equipment_operating_conditions import (
    extract_narrative,
)
from src.constants.Extractions import Extractions
from src.graphql.utils import update_document_status, update_document_junior_status

get_equipment_operating_data = extract_narrative.get_equipment_operating_data


async def handle_EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA(
    params,
):  # pylint: disable=invalid-name
    """
    Extract Process Narrative Rag Junior Data"""
    try:
        bucket_name = params["bucket_name"]
        extract_type = params["extract_type"]
        # pid_connections_json_path = (
        #     "public/"
        #     + params["plant_id"]
        #     + "/DOCS/PROCESS_NARRATIVE/"
        #     + params["document_id"]
        #     + "/p&id_source_destination_connection.json"
        # )
        if "model_name" in params:
            model_name = params["model_name"]
        else:
            model_name = "gpt-4o"

        if extract_type == Extractions.PROCESS_NARRATIVE_STREAM_CONDITION_EXTRACTION:
            logger.info(
                f"Extracting Process Narrative Rag Junior Data for {extract_type}"
            )
            adm_json_path = (
                params["plant_id"]
                + "/documents/process_narrative/"
                + params["document_id"]
                + "/"
                + params["document_id"]
                + ".PROCESS_NARRATIVE.junior.adm.json"
            )
            input_files_path = {
                # "pid_source_destination_connection_path": pid_connections_json_path,
                "bucket_name": bucket_name,
                "plant_id": params["plant_id"],
                "document_id": params["document_id"],
            }
            await get_data(input_files_path, model_name, adm_json_path)
            await update_document_status(params["document_id"], "GENERATED")
            await update_document_junior_status(params["document_id"], "GENERATED")
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "success": True,
                        "msg": "Extracted Process narrative using junior and rag successfully",
                        "path": adm_json_path,
                    }
                ),
            }
        if (
            extract_type
            == Extractions.PROCESS_NARRATIVE_EQUIPMENT_OPERATING_CONDITION_EXTRACTION
        ):
            logger.info("Process Narrative Equipment Operating Condition Extraction")
            adm_json_path = (
                params["plant_id"]
                + "/documents/process_narrative/"
                + params["document_id"]
                + "/"
                + params["document_id"]
                + ".PROCESS_NARRATIVE.oc.junior.adm.json"
            )
            input_files_path = {
                "bucket_name": bucket_name,
                "plant_id": params["plant_id"],
                "document_id": params["document_id"],
            }
            await get_equipment_operating_data(
                input_files_path,
                model_name,
                adm_json_path,
            )
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "success": True,
                        "msg": "Extracted Process narrative equipment operating"
                        + "condition using junior and rag successfully",
                        "path": adm_json_path,
                    }
                ),
            }

    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.error(
            "Error in handle_EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA: %s", str(e)
        )
        await update_document_status(params["document_id"], "ERROR")
        await update_document_junior_status(params["document_id"], "ERROR")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA: {str(e)}",
                }
            ),
        }
