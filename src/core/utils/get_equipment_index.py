"""This module contains functions for extracting equipment data."""

import os
import requests
import pandas as pd
from src.utils.log import logger
from src.utils.s3_download_upload import save_df_to_storage
from src.utils.token import get_token

# EXTRACT_EQUIPMENT_INDEX_LAMBDA_ARN = os.environ.get(
#     "EXTRACT_EQUIPMENT_INDEX_LAMBDA_ARN", ""
# )


# def invoke_equipment_connectivity_index_lambda(plant_id):
#     """Invoke ExtractTable Lambda for a Page"""
#     payload = {
#         "step": "GET_REPORT",
#         "payload": {
#             "plant_id": plant_id,
#             "report_id": "EQUIPMENT_CONNECTIVITY_INDEX",
#             "drawing_numbers": [],
#         },
#     }
#     logger.info(f"Payload for ExtractTable Lambda: {payload}")
#     _, _, lambda_client = setup_aws_clients()
#     logger.info("Invoking ExtractTable Lambda...")
#     response = invoke_lambda(
#         lambda_client=lambda_client,
#         function_name=EXTRACT_EQUIPMENT_INDEX_LAMBDA_ARN,
#         payload=json.dumps(payload),
#     )
#     logger.info("Response generated for Lambda.")
#     response_payload = response["Payload"].read()
#     response_data = json.loads(response_payload.decode("utf-8"))
#     data = (
#         json.loads(response_data["data"])
#         if isinstance(response_data["data"], str)
#         else response_data["data"]
#     )
#     return data


# def invoke_equipment_index_lambda(plant_id):
#     """Invoke ExtractTable Lambda for a Page"""
#     payload = {
#         "step": "GET_REPORT",
#         "payload": {
#             "plant_id": plant_id,
#             "report_id": "EQUIPMENT_CONNECTIVITY_INDEX",
#             "drawing_numbers": [],
#         },
#     }
#     logger.info(f"Payload for ExtractTable Lambda: {payload}")
#     _, _, lambda_client = setup_aws_clients()
#     logger.info("Invoking ExtractTable Lambda...")
#     response = invoke_lambda(
#         lambda_client=lambda_client,
#         function_name=EXTRACT_EQUIPMENT_INDEX_LAMBDA_ARN,
#         payload=json.dumps(payload),
#     )
#     logger.info("Response generated for Lambda.")
#     response_payload = response["Payload"].read()
#     response_data = json.loads(response_payload.decode("utf-8"))
#     data = (
#         json.loads(response_data["data"])
#         if isinstance(response_data["data"], str)
#         else response_data["data"]
#     )
#     return data


def invoke_equipment_index_lambda(plant_id):
    """Invoke ExtractTable Lambda"""
    logger.info("Invoke ExtractTable Lambda")
    extract_equipment_index_lambda_url = os.environ.get(
        "EXTRACT_EQUIPMENT_INDEX_LAMBDA_URL", ""
    )
    artisan_auth_token = get_token()
    if not extract_equipment_index_lambda_url:
        raise ValueError(
            "EXTRACT_EQUIPMENT_INDEX_LAMBDA_URL environment variable is not set"
        )

    payload = {
        "step": "GET_REPORT",
        "payload": {
            "plant_id": plant_id,
            "report_id": "EQUIPMENT_INDEX",
            "artisan_auth_token": artisan_auth_token,
        },
    }
    logger.info(f"Payload for ExtractTable Lambda: {payload}")
    logger.info("Invoking ExtractTable Lambda...")
    headers = {
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            url=extract_equipment_index_lambda_url,
            json=payload,
            headers=headers,
            timeout=300,
        )
    except Exception as e:
        logger.error(f"Error invoking ExtractTable Lambda: {e}")
        raise e

    logger.info("Response generated for Lambda.")
    response.raise_for_status()
    response_payload = response.json()

    if response_payload.get("success"):
        logger.info(response_payload)
        data = response_payload.get("data")
        return data

    logger.error(f"Lambda invocation failed with payload: {response_payload}")

    return None


def is_stand_by(entry):
    """Check if the given entry is a stand_by entry for both source and destination"""
    if entry["stand_by_equipment"] == "false":
        return False
    return True


def is_duplicate(entry_list, new_entry):
    """Check if the given entry is a duplicate entry"""
    for entry in entry_list:
        if (
            entry["asset_name"] == new_entry["asset_name"]
            and entry["asset_tag"] == new_entry["asset_tag"]
            and entry["asset_class"] == new_entry["asset_class"]
        ):
            return True
    return False


async def save_process_equipment_index(bucket_name, plant_id, asset_list_path):
    """
    Extracts the equipment index file.
    """
    logger.info("Extracting equipment index data...")
    equipment_index_data = invoke_equipment_index_lambda(plant_id)
    # with open("equipment_index.json", "w", encoding="utf-8") as f:
    #     json.dump(equipment_index_data, f, indent=4)
    if not equipment_index_data:
        logger.error("Equipment index data is either unavailable or empty")
        raise ValueError("Equipment index data is either unavailable or empty")
    logger.info("Processing equipment index data...")
    equipment_data = []
    for entry in equipment_index_data:
        #     "name": null,
        # "type": "PUMP PROCESS",
        # "tag": "PBA-8420/21/22",
        # id,asset_name,asset_tag,asset_class,process_narrative
        try:
            if not entry.get("name") or not entry.get("tag") or not entry.get("type"):
                logger.warning(
                    f"Skipping entry due to missing required fields: {entry}"
                )
                continue

            new_entry = {
                # "id": entry.get("id"),  # entry["ID"],
                "asset_name": entry["name"],
                "asset_tag": entry["tag"],
                "asset_class": entry["type"],
            }
        except KeyError as e:
            raise KeyError(f"The key {e} is missing from the entry dictionary.") from e

        if not is_stand_by(entry) and not is_duplicate(equipment_data, new_entry):
            equipment_data.append(new_entry)

    df = pd.DataFrame(equipment_data)
    await save_df_to_storage(bucket_name, asset_list_path, df)

    logger.info(f"Extracted data has been saved to {asset_list_path}")
