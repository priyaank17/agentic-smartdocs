"""This module contains functions for extracting source and destination data."""
import json
from src.utils.log import logger
from src.utils.get_equipment_index import (
    invoke_equipment_index_lambda,
)

from src.utils.storage_utils import (
    upload_file_to_storage
)


def is_stand_by(entry):
    """Check if the given entry is a stand_by entry for both source and destination"""
    if (
        entry["is_source_stand_by_equipment"] is False
        and entry["is_destination_stand_by_equipment"] is False
    ):
        return False
    return True


def is_duplicate(entry, existing_data):
    """
    Check if the given entry is a duplicate of an existing entry.
    """
    for existing_entry in existing_data:
        if (
            entry["source_equipment_tag"] == existing_entry["source_equipment_tag"]
            and entry["destination_equipment_tag"]
            == existing_entry["destination_equipment_tag"]
            and entry["source_asset_name"] == existing_entry["source_asset_name"]
            and entry["destination_asset_name"]
            == existing_entry["destination_asset_name"]
        ):
            return True
    return False


def load_equipment_connectivity_index(plant_id):
    """
    Loads the equipment connectivity index file from S3.
    """
    equipment_connectivity_index_data = invoke_equipment_index_lambda(plant_id)
    # invoke_equipment_connectivity_index_lambda(plant_id)

    return equipment_connectivity_index_data


async def process_equipment_connectivity(
    bucket_name, plant_id, pid_connections_json_path
):
    """
    Extracts the source and destination equipment connectivity index file.
    """
    equipment_connectivity_index_data = load_equipment_connectivity_index(plant_id)
    source_destination_data = []
    for entry in equipment_connectivity_index_data:
        try:
            new_entry = {
                "source_equipment_tag": entry["source_equipment_tag"],
                "destination_equipment_tag": entry["destination_equipment_tag"],
                "source_asset_name": entry["source_equipment_description"],
                "destination_asset_name": entry["destination_equipment_description"],
                "material_stream_tag": entry.get("material_stream_tag"),
            }
        except KeyError as e:
            raise KeyError(f"The key {e} is missing from the entry dictionary.") from e

        if not is_stand_by(entry) and not is_duplicate(
            new_entry, source_destination_data
        ):
            source_destination_data.append(new_entry)
    await upload_file_to_storage(
        bucket_name,
        pid_connections_json_path,
        json.dumps(source_destination_data),
    )
    logger.info(f"Extracted data has been saved to {pid_connections_json_path}")
