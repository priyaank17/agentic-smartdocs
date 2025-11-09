"""Postprocess sensor property data."""
import re

# import pandas as pd
from src.utils.log import logger
import src.process_narrative.postprocessing.utils as ut
from src.utils.s3_download_upload import read_csv_from_storage


def add_verification(data):
    """Add verification to json data."""
    for connection in data:
        connection["flow_rate"]["verification"] = None
        connection["temperature"]["verification"] = None
        connection["pressure"]["verification"] = None
    return data


def convert_to_numeric(value):
    """Convert value to numeric."""
    value = re.sub(r"[^\d.-]", "", value)
    return float(value) if "." in value else int(value)


def extract_unique_values_sensor_property(paragraph, sensor_property):
    """Extract unique values of sensor property from paragraph."""
    logger.info(f"INIT: extract unique {sensor_property} values from narrative.")
    units = {
        "flow_rate_unit": "MMSCFD",
        "pressure_unit": "psig",
        "temperature_unit": "\u00b0F",
    }
    patterns = {
        "flow_rate": r"(\d+\.?\d*)\s*" + re.escape(units["flow_rate_unit"]),
        "pressure": r"(\d+)\s*" + re.escape(units["pressure_unit"]),
        "temperature": r"(-?\d+)\s*" + re.escape(units["temperature_unit"]),
    }
    value_pattern = patterns.get(sensor_property)
    values = re.findall(value_pattern, paragraph)

    and_to_pattern = {
        "flow_rate": r"(\d+\.?\d*)\s*(?:to|and)\s*(\d+\.?\d*)\s*"
        + re.escape(units["flow_rate_unit"]),
        "pressure": r"(\d+)\s*(?:to|and)\s*(\d+)\s*"
        + re.escape(units["pressure_unit"]),
        "temperature": r"(-?\d+)\s*(?:to|and)\s*(-?\d+)\s*"
        + re.escape(units["temperature_unit"]),
    }
    value_and_to_pattern = and_to_pattern.get(sensor_property)
    and_to_values = re.findall(value_and_to_pattern, paragraph)
    values.extend([f"{value1} {sensor_property}" for value1, _ in and_to_values])
    unique_values = list(set(convert_to_numeric(value) for value in values))
    logger.info(f"DONE: extracted unique {sensor_property} values from narrative.")
    return unique_values


async def extract_value_assets(
    expected_asset_csv_s3, bucket_name, sensor_property, narrative_csv_path
):
    """Extract sensor property value from narrative for all assets."""
    logger.info(f"INIT: extract {sensor_property} value from narrative for all assets.")
    expected_values = {}
    df = await read_csv_from_storage(bucket=bucket_name, path=expected_asset_csv_s3)
    narrative = await read_csv_from_storage(bucket=bucket_name, path=narrative_csv_path)
    narrative_string = narrative.to_csv(index=False)
    for _, row in df.iterrows():
        asset_name = row["asset_name"]
        narrative = narrative_string
        unique_values = extract_unique_values_sensor_property(
            narrative, sensor_property
        )
        expected_values[asset_name] = unique_values
    logger.info(
        f"DONE: extracted {sensor_property} value from narrative for all assets."
    )
    return expected_values


def validate_and_update_sensor_property_value(
    updated_received_assets_connections,
    sensor_property,
    bucket_name,
    expected_asset_csv_s3,
    narrative_csv_path,
):
    """Validate and update sensor property value."""
    logger.info(f"Validating and updating {sensor_property} values")
    expected_values = extract_value_assets(
        expected_asset_csv_s3, bucket_name, sensor_property, narrative_csv_path
    )
    for received_asset in updated_received_assets_connections:
        asset_name = ut.get_asset_name_from_id(
            received_asset, bucket_name, expected_asset_csv_s3
        )
        expected_val = expected_values.get(asset_name, {})
        value = received_asset[sensor_property]["value"]
        if (value not in expected_val) and (value is not None):
            received_asset[sensor_property]["verification"] = False
            received_asset[sensor_property]["value"] = None
        else:
            received_asset[sensor_property]["verification"] = True
    logger.info(f"Validated and updated {sensor_property} values")


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
    """Remove verification from json data."""
    if isinstance(json_data, dict):
        json_data.pop("verification", None)
        for _, value in json_data.items():
            remove_verification(value)
    elif isinstance(json_data, list):
        for item in json_data:
            remove_verification(item)
