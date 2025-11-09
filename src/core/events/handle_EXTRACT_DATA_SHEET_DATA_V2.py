"""This module consists of functions for extracting data sheet data"""

import json
import os
from src.utils.log import logger
from src.graphql.utils import update_document_status
from src.constants.Extractions import Extractions
from src.data_sheets_v2.extract_table_data.extract import (
    extract_table_data,
    extract_second_shot_table_data,
    extract_table_by_id,
)
from src.data_sheets_v2.get_raw_json.get_combined_json import (
    extract_raw_data_json,
)
from src.data_sheets_v2.get_adm_json.get_nodes_folder.adm import (
    get_adm_json,
)
from src.data_sheets_v2.get_adm_json.property_mapping_loader import (
    prepare_asset_mapping,
)
from src.utils.s3_download_upload import (
    # load_into_memory,
    save_json_to_storage,
    load_json_from_storage,
    check_file_in_storage,
)

from src.utils.storage_utils import (
    upload_file_to_storage,
)
from src.data_sheets_v2.classification.get_equipment_name import (
    get_asset_type,
)
from src.data_sheets_v2.prepare_input.get_input_data import (
    # prepare_table_extraction_data,
    prepare_table_extraction_data_vision,
)


# pylint: disable=invalid-name, too-many-branches, too-many-statements
async def handle_EXTRACT_DATA_SHEET_DATA_V2(params):  # noqa: C901
    """Extract Data Sheet Data"""
    try:
        # is_local = True
        if os.getenv("LOCAL") is True:
            logger.info("Using local environment")
        else:
            logger.info("Using cloud environment")

        logger.info("Extracting Data Sheet Data")
        plant_id = params.get("plant_id")
        bucket_name = params.get("bucket_name", "default-bucket-name")
        extract_type = params.get("extract_type")
        document_id = params.get("document_id")
        path = f"{plant_id}/documents/data_sheet/{document_id}"
        input_data_path = f"{path}/input_data.json"
        adm_path = f"{plant_id}/adms/data_sheet"
        pdf_path = f"{plant_id}/user_uploaded_documents/{document_id}"
        data_sheet_adm_path = adm_path + "/" + document_id + ".data_sheet.adm.json"
        # ".DATA_SHEET.adm.json"
        raw_data_json_path = f"{path}/{document_id}.data_sheet.raw.json"
        model_name = "gpt-4o"
        table_info = {
            "document_id": document_id,
            "plant_id": plant_id,
            "model_name": model_name,
        }

        if not all([extract_type, document_id, input_data_path]):
            raise ValueError("Missing required parameters")

        if extract_type == Extractions.INITIAL_DATA_SHEET_EXTRACTION:
            logger.info(f"Generate empty adm json file {extract_type}")
            await upload_file_to_storage(
                bucket_name,
                data_sheet_adm_path,
                json.dumps({}),
            )
            logger.info(
                f"Extracting Input data from Data Sheet  for data sheet digitization {extract_type}"
            )
            if not await check_file_in_storage(bucket_name, input_data_path):
                input_data = await prepare_table_extraction_data_vision(
                    bucket_name, path, document_id, plant_id
                )
                await save_json_to_storage(bucket_name, input_data_path, input_data)
            else:
                logger.info(f"Input data already exists at {input_data_path}")
            await update_document_status(document_id, "GENERATED")

        elif extract_type == Extractions.DATA_SHEET_TABLE_EXTRACTION:
            logger.info(f"Extracting Data Sheet Data for {extract_type}")
            await extract_table_data(
                input_data_path,
                table_info,
                bucket_name,
                save_local=os.getenv("LOCAL") is True,
            )
        elif extract_type == Extractions.DATA_SHEET_SECOND_SHOT_TABLE_EXTRACTION:
            logger.info(f"Extracting Data Sheet Data for {extract_type}")
            await extract_second_shot_table_data(
                input_data_path, bucket_name, table_info
            )
        elif extract_type == Extractions.DATA_SHEET_GENERATE_RAW_JSON:
            logger.info(f"Extracting RAW Data Sheet Data for {extract_type}")
            await extract_raw_data_json(
                input_data_path, bucket_name, raw_data_json_path, plant_id, document_id
            )
        elif extract_type == Extractions.DATA_SHEET_INPUT_DATA_EXTRACTION:
            logger.info(
                f"Extracting Input data from Data Sheet Data for {extract_type}"
            )
            if not check_file_in_storage(bucket_name, input_data_path):
                # if check_file_in_storage(bucket_name, input_data_path):
                input_data = await prepare_table_extraction_data_vision(
                    bucket_name, path, document_id, plant_id
                )
                await save_json_to_storage(bucket_name, input_data_path, input_data)
            else:
                logger.info(f"Input data already exists at {input_data_path}")

        elif extract_type == Extractions.DATA_SHEET_INDIVIDUAL_TABLE_EXTRACTION:
            table_id = params.get("table_id")
            if not table_id:
                raise ValueError("table_id is required for individual table extraction")

            logger.info(f"Extracting Data Sheet Data for {extract_type}")

            table_info["table_id"] = table_id
            await extract_table_by_id(input_data_path, bucket_name, table_info)
            logger.info(f"Extracting Data Sheet Data for {extract_type}")
        elif extract_type == Extractions.DATA_SHEET_GENERATE_ADM:
            logger.info(f"Extracting Data Sheet ADM for {extract_type}")
            asset_type = await get_asset_type(bucket_name, pdf_path)
            standard_property_field_mapping_df = await prepare_asset_mapping(asset_type)
            raw_data = await load_json_from_storage(bucket_name, raw_data_json_path)
            adm_data = await get_adm_json(
                raw_data, document_id, standard_property_field_mapping_df
            )
            await save_json_to_storage(bucket_name, data_sheet_adm_path, adm_data)
            await update_document_status(document_id, "GENERATED")

        else:
            await update_document_status(document_id, "ERROR")
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "success": False,
                        "msg": f"Invalid extract_type: {extract_type}",
                    }
                ),
            }

        if os.getenv("LOCAL") is True:
            await update_document_status(document_id, "GENERATED")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "success": True,
                    "msg": f"Data Sheet Data extracted successfully for {extract_type}",
                }
            ),
        }

    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error(f"Error in handle_DATA_SHEET_EXTRACTION V2: {str(e)}")
        if os.getenv("LOCAL") is True:
            await update_document_status(document_id, "ERROR")
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "success": False,
                    "msg": f"Error in handle_DATA_SHEET_EXTRACTION: {str(e)}",
                }
            ),
        }
