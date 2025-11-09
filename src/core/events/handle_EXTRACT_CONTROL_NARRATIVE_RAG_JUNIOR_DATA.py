"""This module consists of functions for extracting control narrative data"""

import json
from src.utils.log import logger
from src.graphql.utils import update_document_status, update_document_junior_status
from src.control_narrative_rag_junior.connection_data_extraction.extract_control_narrative import (
    get_control_instrument_adm,
    get_control_loop_adm
)


async def handle_EXTRACT_CONTROL_NARRATIVE_RAG_JUNIOR_DATA(params):  # pylint: disable=invalid-name
    """
    handles the extraction of control narrative data.
    """
    try:
        bucket_name = params["bucket_name"]
        if "model_name" in params:
            model_name = params["model_name"]
        else:
            model_name = "gpt-4o"
        control_loop_adm_json_path = (
            params["plant_id"]
            + "/documents/control_narrative/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".CONTROL_NARRATIVE.junior.cl.adm.json"
        )
        instrument_adm_json_path = (
            params["plant_id"]
            + "/documents/control_narrative/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".CONTROL_NARRATIVE.junior.inst.adm.json"
        )
        input_files_path = {
            "bucket_name": bucket_name,
            "plant_id": params["plant_id"],
            "document_id": params["document_id"],
        }
        await get_control_loop_adm(
            input_files_path, control_loop_adm_json_path, model_name
        )
        logger.info("Control Loop extracted successfully")
        await get_control_instrument_adm(
            input_files_path, instrument_adm_json_path, model_name
        )
        logger.info("Control Instrument extracted successfully")
        await update_document_status(params["document_id"], "GENERATED")
        await update_document_junior_status(params["document_id"], "GENERATED")
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "msg": "Control narrative extracted successfully",
                    "control_loop_path": control_loop_adm_json_path,
                    "instrument_path": instrument_adm_json_path,
                }
            ),
        }
    except Exception as e:  # pylint: disable=W0718
        logger.error(f"Error in handle_CONTROL_NARRATIVE_RAG_JUNIOR_DATA: {str(e)}")
        await update_document_status(params["document_id"], "ERROR")
        await update_document_junior_status(params["document_id"], "ERROR")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_EXTRACT_CONTROL_NARRATIVE_RAG_JUNIOR_DATA: {str(e)}",
                }
            )
        }
