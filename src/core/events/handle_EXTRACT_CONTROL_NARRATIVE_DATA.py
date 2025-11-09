"""This module consists of functions for extracting control narrative data"""

import json
from src.control_narrative_lambda.control_narrative.extract_control_narrative_data import (
    extract_control_narrative_data,
)
from src.utils.log import logger
from src.graphql.utils import update_document_status
from src.control_narrative_lambda.control_narrative.generate_adm import (
    generate_adm,
)


async def handle_EXTRACT_CONTROL_NARRATIVE_DATA(params):  # pylint: disable=invalid-name
    """
    Asynchronously handles the extraction of control narrative data.

    Args:
        params (dict): A dictionary containing the following keys:
            - bucket_name (str): The name of the S3 bucket.
            - plant_id (str): The ID of the plant.
            - document_id (str): The ID of the document.

    Returns:
        dict: A dictionary indicating the success of the operation.
        The dictionary has the following keys:
            - success (bool): True if the operation is successful, False otherwise.
            - msg (str): An error message if the operation fails, None otherwise.
    """
    try:
        bucket_name = params["bucket_name"]
        input_data_path = (
            params["plant_id"]
            + "/documents/control_narrative/"
            + params["document_id"]
            + "/input_data.json"
        )
        reconciled_control_loops_path = (
            params["plant_id"]
            + "/documents/control_narrative/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".CONTROL_NARRATIVE.cl.adm.json"
        )
        key_aggregated_control_loops = (
            params["plant_id"]
            + "/documents/control_narrative/"
            + params["document_id"]
            + "/aggregated_control_loops.json"
        )
        key_aggregated_instruments = (
            params["plant_id"]
            + "/documents/control_narrative/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".CONTROL_NARRATIVE.inst.adm.json"
        )
        key_aggregated_info = {
            "key_aggregated_control_loops": key_aggregated_control_loops,
            "key_aggregated_instruments": key_aggregated_instruments,
        }
        await extract_control_narrative_data(
            bucket_name=bucket_name,
            input_data_path=input_data_path,
            reconciled_control_loops_path=reconciled_control_loops_path,
            key_aggregated_info=key_aggregated_info,
        )
        await generate_adm(
            bucket_name=bucket_name,
            data_path=reconciled_control_loops_path,
            config_data_key=input_data_path,
        )
        await generate_adm(
            bucket_name=bucket_name,
            data_path=key_aggregated_instruments,
            config_data_key=input_data_path,
        )
        await update_document_status(params["document_id"], "GENERATED")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "msg": "Control narrative extracted successfully",
                    "control_loop_path": reconciled_control_loops_path,
                    "instrument_path": key_aggregated_instruments,
                }
            ),
        }
    except Exception as e:  # pylint: disable=W0718
        logger.error(f"Error in handle_CONTROL_NARRATIVE_DATA: {str(e)}")
        await update_document_status(params["document_id"], "ERROR")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_EXTRACT_CONTROL_NARRATIVE_DATA: {str(e)}",
                }
            )
        }
