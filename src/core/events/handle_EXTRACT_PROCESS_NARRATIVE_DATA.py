"""This module consists of functions for extracting process narrative data"""

import json
from src.utils.log import logger
from src.process_narrative.extract_data import extract_data
from src.graphql.utils import update_document_status

# from src.process_narrative.create_narrative_csv import (
#     create_narrative_csv,
# )
from src.utils.s3_download_upload import read_csv_from_storage
from src.process_narrative.extract_ocr import create_narrative_csv
from src.utils.storage_utils import (
    fetch_file_via_adapter
)


async def handle_EXTRACT_PROCESS_NARRATIVE_DATA(params):  # pylint: disable=invalid-name
    """
    Extract Process Narrative Data"""
    try:
        bucket_name = params["bucket_name"]
        logger.info("Reading Asset JSON from storage")
        asset_csv_path = (
            params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/assets_table.csv"
        )
        # asset_json_path = (
        #     params["plant_id"] + "/documents/equipment_narrative_index.json"
        # )
        # s3_response = await s3.get_file(
        # GetFileRequest(bucket=bucket_name, path=asset_json_path))
        # if bucket_name:
        #     s3_response = await fetch_cloud_file_via_adapter(
        # cloud_storage,
        # bucket_name,
        # asset_json_path)
        # else:
        #     s3_response = await read_local_file_via_adapter(
        # local_storage,
        # asset_json_path)
        # s3_response = s3_response["Body"].read().decode("utf-8")
        # logger.info("Reading Asset JSON from storage completed")
        # asset_json_data_before_processing = json.loads(
        #     s3_response
        # )
        # df = pd.DataFrame(asset_json_data_before_processing)
        # df.rename(
        #     columns={"tag": "asset_tag", "description": "asset_name"}, inplace=True
        # )
        # df.drop(["drawing_number", "uuid", "narrative_text"], axis=1, inplace=True)
        # asset_csv_data = df.to_csv(index=False)
        # put_object_in_storage(
        #     data=asset_csv_data.encode("utf-8"),
        #     bucket=params["bucket_name"],
        #     destination="public/"
        #     + params["plant_id"]
        #     + "/documents/process_narrative/"
        #     + params["document_id"]
        #     + "/assets_table.csv",
        # )
        # if bucket_name:
        #     await upload_file_to_cloud_via_adapter(
        # cloud_storage,
        # bucket_name,
        # params["plant_id"] + "/documents/process_narrative/" +
        # params["document_id"] + "/assets_table.csv", asset_csv_data.encode("utf-8")
        # )
        # else:
        #     await write_local_file_via_adapter(
        # local_storage,
        # params["plant_id"] + "/documents/process_narrative/" +
        # params["document_id"] + "/assets_table.csv", asset_csv_data.encode("utf-8"))
        # logger.info("assets_table is created and uploaded to s3")
        # logger.info("Reading Asset CSV from s3")
        narrative_csv_path = (
            params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/narrative_paragraphs.csv"
        )
        # input_pdf_s3_path = (
        #     params["plant_id"] + "/documents/" + params["document_id"]
        # )
        input_bounding_box_config_path = (
            params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/input_data.json"
        )
        await create_narrative_csv(
            bucket_name,
            input_bounding_box_config_path,
        )
        narrative_text = await read_csv_from_storage(
            bucket=bucket_name, path=narrative_csv_path
        )
        # if bucket_name:
        #     narrative_text = await fetch_cloud_file_via_adapter(
        # cloud_storage,bucket_name, narrative_csv_path)
        # else:
        #     narrative_text = await read_local_file_via_adapter(local_storage, narrative_csv_path)
        # narrative_text = pd.read_csv(narrative_text["Body"])
        asset_bucket = params["bucket_name"]
        bucket_name = params["bucket_name"]
        pnid_connections_json_path = (
            params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/p&id_source_destination_connection.json"
        )
        response = await fetch_file_via_adapter(bucket_name, pnid_connections_json_path)
        # pid_source_destination_connection_data = json.loads(
        #     response.data.data
        # )
        pid_source_destination_connection_data = response
        extracted_json_s3_file_key = (
            params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/extracted_data.json"
        )
        connections_json_file_key = (
            params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/connections.json"
        )
        if "model_name" in params:
            model_name = params["model_name"]
        else:
            model_name = "gpt-4"
        asset_text = await read_csv_from_storage(bucket=asset_bucket, path=asset_csv_path)
        # if asset_bucket:
        #     asset_text = await fetch_cloud_file_via_adapter(
        # cloud_storage,
        # asset_bucket,
        # asset_csv_path
        # )
        # else:
        #     asset_text = await read_local_file_via_adapter(local_storage, asset_csv_path)
        # asset_text = pd.read_csv(asset_text["Body"])
        post_process_connection_path = (
            params["plant_id"]
            + "/documents/process_narrative/"
            + params["document_id"]
            + "/"
            + params["document_id"]
            + ".PROCESS_NARRATIVE.adm.json"
        )
        extracted_json_file_key = extracted_json_s3_file_key
        process_narrative_args = (
            narrative_text,
            asset_text,
            bucket_name,
            pnid_connections_json_path,
            extracted_json_file_key,
            connections_json_file_key,
            model_name,
            pid_source_destination_connection_data,
            post_process_connection_path,
            input_bounding_box_config_path,
        )
        await extract_data(
            process_narrative_args,
        )
        await update_document_status(params["document_id"], "GENERATED")
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "msg": "Process narrative extracted successfully",
                    "path": post_process_connection_path,
                }
            ),
        }
    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.error("Error in handle_EXTRACT_PROCESS_NARRATIVE_DATA: %s", str(e))
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
