"""Extract HMB document data."""

import json
from src.graphql.utils import update_document_status
from src.utils.log import logger
from src.local_execution.hmb_documents.extract_hmb_data import extract_tables_from_pdf


async def handle_EXTRACT_HMB_DOCUMENT_DATA(params):  # pylint: disable=invalid-name
    """."""
    try:
        logger.info("INIT: handle_EXTRACT_HMB_DOCUMENT_DATA")
        bucket_name = params["bucket_name"]
        pdf_s3_key = params["plant_id"] + "/documents/" + params["document_id"]
        output_directory = (
            params["plant_id"] + "/documents/hmb/" + params["document_id"]
        )
        table_json_path = (
            params["plant_id"]
            + "/documents/hmb/"
            + params["document_id"]
            + "/input_data.json"
        )
        output_json_path = (
            params["plant_id"]
            + "/documents/hmb/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".HMB.adm.json"
        )
        await extract_tables_from_pdf(
            bucket_name=bucket_name,
            pdf_file_path=pdf_s3_key,
            table_json_path=table_json_path,
            output_directory=output_directory,
            output_json_path=output_json_path,
        )
        await update_document_status(params["document_id"], "GENERATED")
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "msg": "HMB document data extracted successfully",
                    "path": output_json_path,
                }
            ),
        }
    except Exception as e:  # pylint: disable=W0718
        logger.error(f"Error in handle_EXTRACT_HMB_DOCUMENT_DATA: {str(e)}")
        await update_document_status(params["document_id"], "ERROR")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_EXTRACT_HMB_DOCUMENT_DATA: {str(e)}",
                }
            ),
        }
