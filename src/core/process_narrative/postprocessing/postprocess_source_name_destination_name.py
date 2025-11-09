"""This module contains functions to postprocess the source and destination names."""
from fuzzywuzzy import fuzz
from src.utils.log import logger
import src.process_narrative.postprocessing.utils as ut


def rename_attribute_with_best_match(
    received_assets_connections, asset_name_list, attribute_type
):
    """Rename attribute with best match."""
    logger.info("INIT: rename attribute_with_best_match")
    for connection in received_assets_connections:
        expected_attribute_val_name = connection.get(attribute_type, "").lower()
        best_match = None
        best_similarity = 0
        for asset_name in asset_name_list:
            similarity = fuzz.ratio(asset_name.lower(), expected_attribute_val_name)
            if similarity >= 90:
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = asset_name
        if best_match is not None:
            connection[attribute_type] = best_match
    logger.info("DONE: renamed attribute_with_best_match")


def filter_source_destination_name_property(
    received_assets_connections, attribute_type, bucket_name, expected_asset_csv_s3
):
    """Filter source and destination name property."""
    logger.info(f"INIT: filter {attribute_type}")
    for connection in received_assets_connections:
        asset_name = ut.get_asset_name_from_id(
            connection, bucket_name, expected_asset_csv_s3
        )
        connection_type = connection["connection_type"]
        if (connection_type == "IN_LET") and (
            attribute_type == "destination_asset_name"
        ):
            connection[attribute_type] = asset_name
        elif (connection_type == "OUT_LET") and (attribute_type == "source_asset_name"):
            connection[attribute_type] = asset_name
    logger.info(f"DONE: filter {attribute_type}")


def filter_unverified_connections(updated_received_assets_connections):
    """Filter unverified connections."""
    logger.info("Filtering unverified connections")
    filtered_connections = []
    for connection in updated_received_assets_connections:
        flow_rate_verification = connection.get("flow_rate", {}).get(
            "verification", False
        )
        temperature_verification = connection.get("temperature", {}).get(
            "verification", False
        )
        pressure_verification = connection.get("pressure", {}).get(
            "verification", False
        )
        flow_rate_value = connection.get("flow_rate", {}).get("value")
        temperature_value = connection.get("temperature", {}).get("value")
        pressure_value = connection.get("pressure", {}).get("value")
        a = (
            not flow_rate_verification
            and not temperature_verification
            and not pressure_verification
        ) or (
            (
                not flow_rate_verification
                or not temperature_verification
                or not pressure_verification
            )
            and (
                flow_rate_value is None
                and temperature_value is None
                and pressure_value is None
            )
        )
        if a:
            continue
        filtered_connections.append(connection)
    updated_received_assets_connections.clear()
    updated_received_assets_connections.extend(filtered_connections)
    del filtered_connections
    logger.info("Unverified connections filtered")


def remove_verification(json_data):
    """Remove the verification key from the JSON data."""
    if isinstance(json_data, dict):
        json_data.pop("verification", None)
        for _, value in json_data.items():
            remove_verification(value)
    elif isinstance(json_data, list):
        for item in json_data:
            remove_verification(item)
