"""v"""

import json
from src.utils.storage_utils import (
    upload_file_to_storage
)
from src.utils.log import logger
from src.control_narrative_rag_junior.connection_data_extraction import (
    extract_control_loops_narrative,
    generate_control_narrative_adm,
    extract_control_instrument_narrative,
)

get_control_loops_data = extract_control_loops_narrative.get_control_loops_data
get_control_instrument_data = (
    extract_control_instrument_narrative.get_control_instrument_data
)

get_control_narrative_control_loops_adm = (
    generate_control_narrative_adm.get_control_narrative_control_loops_adm
)

get_control_narrative_instrument_adm = (
    generate_control_narrative_adm.get_control_narrative_instrument_adm
)


async def get_control_loop_adm(
    input_files_path, control_loop_adm_json_path, model_name, save_to_local=False
):
    """Get data"""
    bucket_name = input_files_path.get("bucket_name")
    document_id = input_files_path.get("document_id")
    plant_id = input_files_path.get("plant_id")

    if not all([bucket_name, document_id, plant_id]):
        raise ValueError(
            "Missing required parameters: bucket_name, document_id, or plant_id"
        )

    control_loop_json_data = {
        "meta_data": {},
        "data": [],
    }

    control_loop_data = await get_control_loops_data(
        bucket_name, plant_id, document_id, model_name
    )
    if control_loop_data:
        detailed_control_loop_adm_json_path = control_loop_adm_json_path.replace(
            ".json", ".detailed.json"
        )
        adm_json_data = get_control_narrative_control_loops_adm(
            control_loop_json_data, control_loop_data, document_id
        )

        storage_type = "local" if save_to_local else "storage"
        logger.info(
            "Saving detailed control loop to "
            f"{storage_type} in {detailed_control_loop_adm_json_path}"
        )
        await upload_file_to_storage(
            bucket_name,
            detailed_control_loop_adm_json_path,
            json.dumps(control_loop_data).encode("utf-8"),
        )
        logger.info(f"Saving to {storage_type} {control_loop_adm_json_path}")
        await upload_file_to_storage(
            bucket_name,
            control_loop_adm_json_path,
            json.dumps(adm_json_data).encode("utf-8"),
        )


async def get_control_instrument_adm(
    input_files_path, instrument_adm_json_path, model_name, save_to_local=False
):
    """Get data"""
    bucket_name = input_files_path.get("bucket_name")
    document_id = input_files_path.get("document_id")
    plant_id = input_files_path.get("plant_id")

    control_narrative_instrument_json_data = {
        "meta_data": {},
        "data": [],
    }

    control_narrative_instrument_data = await get_control_instrument_data(
        bucket_name, plant_id, document_id, model_name
    )

    if control_narrative_instrument_data:
        json_data = get_control_narrative_instrument_adm(
            control_narrative_instrument_json_data,
            control_narrative_instrument_data,
            document_id,
        )
        storage_type = "local" if save_to_local else "storage"
        logger.info(
            f"Saving to {storage_type} {instrument_adm_json_path}"
        )
        await upload_file_to_storage(
            bucket_name,
            instrument_adm_json_path,
            json.dumps(json_data).encode("utf-8"),
        )
