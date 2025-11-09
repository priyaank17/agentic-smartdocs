"""This module contains the post_process_data_and_save_to_storage function
 that is used to post-process the extracted data"""

import json
from src.utils.storage_utils import (
    fetch_file_via_adapter,
    upload_file_to_storage
)


async def post_process_data_and_save_to_storage(bucket_name, extracted_json_file_key):
    """Post-process the extracted data and save it to Storage."""
    input_object = await fetch_file_via_adapter(
        bucket_name, extracted_json_file_key
    )
    for entry in input_object:
        entry.setdefault("asset_name", "")
        entry.setdefault("asset_tag", "")
        entry.setdefault("asset_class", "")
        entry.setdefault("asset_id", None)
        entry.setdefault("connections", [])
        entry.setdefault("asset_title", "")

        for connection in entry["connections"]:
            connection.setdefault("connection_type", "")
            connection.setdefault("commodity", "")
            if "flow_rate" not in connection or connection["flow_rate"] is None:
                connection["flow_rate"] = {"value": None, "units": None}
            if "temperature" not in connection or connection["temperature"] is None:
                connection["temperature"] = {"value": None, "units": None}
            if "pressure" not in connection or connection["pressure"] is None:
                connection["pressure"] = {"value": None, "units": None}
            connection.setdefault("source_asset_name", "")
            connection.setdefault("destination_asset_name", "")
            connection.setdefault("narrative_id", None)
            connection.setdefault("id", "")
    await upload_file_to_storage(
        bucket_name,
        extracted_json_file_key,
        json.dumps(input_object, indent=2)
    )
