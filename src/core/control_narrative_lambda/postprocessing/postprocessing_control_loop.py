""""This module is used to post process the control loop of control narrative data"""

import json
from py_unified_cloud_adapter.utils.errors import CloudAdapterException
from src.utils.log import logger
from src.utils.s3_download_upload import load_json_from_storage


def _filter_non_empty_dicts(data):
    """Return a list of dictionaries that have non-empty values for specific keys."""
    filtered_data = [
        d
        for d in data
        if d["process_variable"] and d["controller"] and d["final_control_element"]
    ]
    return filtered_data


def _add_empty_dicts(data, n):
    """Add empty dictionaries for missing narrative IDs up to n."""
    empty_dicts = []
    existing_narratives = set(d["narrative_id"] for d in data)
    for i in range(1, n + 1):
        narrative_id = f"narrative_{i}"
        control_loop_id = f"control_loop_{i}"
        if narrative_id not in existing_narratives:
            empty_dict = {
                "process_variable": [],
                "controller": [],
                "final_control_element": [],
                "description": "",
                "narrative_id": narrative_id,
                "control_loop_id": control_loop_id,
            }
            empty_dicts.append(empty_dict)
            existing_narratives.add(narrative_id)
    return empty_dicts


def _reset_control_loop_ids(data):
    """Reset the control_loop_id for each dictionary in the list based on its index."""
    for i, item in enumerate(data):
        item.pop("control_loop_id", None)
        item["control_loop_id"] = f"control_loop_{i + 1}"


async def get_sample_data_from_file(bucket_name, reconciled_control_loops_path):
    """Fetch JSON data from an S3 bucket and return it as a list of dictionaries."""
    try:
        sample_data = await load_json_from_storage(
            bucket_name, reconciled_control_loops_path
        )
        return sample_data
    except CloudAdapterException:
        logger.info("Credentials not available.")
        return []
    except (json.JSONDecodeError, KeyError):
        logger.info(
            "Error reading the JSON file from S3. Please check the S3 bucket and object key."
        )
        return []


def removed_unnecessary_control_loop(data, n):
    """Remove unnecessary control loops from the data and update the data in the S3 bucket."""
    # sample_data = get_sample_data_from_file(bucket_name, reconciled_control_loops_path)
    if data:
        filtered_data = _filter_non_empty_dicts(data)
        empty_dicts = _add_empty_dicts(filtered_data, n)
        result_data = filtered_data + empty_dicts
        _reset_control_loop_ids(result_data)
        return result_data
    return data
