"""This module is used to post process the connections received from the process narrative."""

from src.utils.log import logger
import src.process_narrative.postprocessing.postprocess_sensor_property as sp
import src.process_narrative.postprocessing.postprocess_source_name_destination_name as sdn
import src.process_narrative.postprocessing.postprocess_connection as connection
import src.process_narrative.postprocessing.utils as ut
from src.utils.s3_download_upload import save_json_to_storage
from src.utils.storage_utils import (
    fetch_file_via_adapter
)


async def _load_config_and_necessary_variables(
    bucket_name, connections_json_file_key, pnid_connections_json_path
):
    """Load config and necessary variables."""
    logger.info("INIT: load_config_and_necessary_variables")
    existing_data = await fetch_file_via_adapter(
        bucket_name, connections_json_file_key)
    pnid_connections_json = await fetch_file_via_adapter(
        bucket_name, pnid_connections_json_path
    )
    logger.info("DONE: load_config_and_necessary_variables")
    return existing_data, pnid_connections_json


def post_process_sensor_property(
    received_assets_connections, bucket_name, expected_asset_csv_s3, narrative_csv_path
):
    """Post process sensor property."""
    logger.info("INIT: post process sensor(temperature, pressure, flow_rate) property")
    updated_received_assets_connections = sp.add_verification(
        received_assets_connections
    )
    sp.validate_and_update_sensor_property_value(
        updated_received_assets_connections,
        "pressure",
        bucket_name,
        expected_asset_csv_s3,
        narrative_csv_path,
    )
    sp.validate_and_update_sensor_property_value(
        updated_received_assets_connections,
        "temperature",
        bucket_name,
        expected_asset_csv_s3,
        narrative_csv_path,
    )
    sp.validate_and_update_sensor_property_value(
        updated_received_assets_connections,
        "flow_rate",
        bucket_name,
        expected_asset_csv_s3,
        narrative_csv_path,
    )
    sp.filter_unverified_connections(updated_received_assets_connections)
    sp.remove_verification(updated_received_assets_connections)
    logger.info(
        "DONE: post processing of sensor(temperature, pressure, flow_rate) property"
    )
    return updated_received_assets_connections


def post_process_source_name_and_destination_name_property(
    updated_received_assets_connections, bucket_name, expected_asset_csv_s3
):
    """Post process source name and destination name property."""
    logger.info("INIT: post process source_name_and_destination_name_property")
    asset_name_list = ut.read_asset_names_from_csv(
        bucket_name, expected_asset_csv_s3, "asset_name"
    )
    sdn.rename_attribute_with_best_match(
        updated_received_assets_connections, asset_name_list, "source_asset_name"
    )
    sdn.rename_attribute_with_best_match(
        updated_received_assets_connections, asset_name_list, "destination_asset_name"
    )
    sdn.filter_source_destination_name_property(
        updated_received_assets_connections,
        "source_asset_name",
        bucket_name,
        expected_asset_csv_s3,
    )
    sdn.filter_source_destination_name_property(
        updated_received_assets_connections,
        "destination_asset_name",
        bucket_name,
        expected_asset_csv_s3,
    )
    logger.info("Done: post processing of source name and destination name property")


async def postprocess_connection(
    received_assets_connections,
    bucket_name,
    expected_asset_csv_s3,
    pnid_connections_json,
):
    """Postprocess connection."""
    logger.info("INIT: postprocess connections")
    await connection.synchronize_and_replicate_connections(
        received_assets_connections,
        bucket_name,
        expected_asset_csv_s3,
        pnid_connections_json,
    )
    logger.info("DONE: postprocess connections")


async def _get_updated_received_data(
    received_assets_connections,
    bucket_name,
    post_process_connection_path,
    input_bounding_box_config_path,
):
    """Get updated received data."""
    logger.info("INIT: get the updated received asset data")
    response = await fetch_file_via_adapter(bucket_name, input_bounding_box_config_path)
    meta_data = response.get("meta_data")
    updated_received_assets_connections = {
        "meta_data": meta_data,
        "connections": received_assets_connections
    }
    # ut.save_json(
    #     updated_received_assets_connections, bucket_name, post_process_connection_path
    # )
    await save_json_to_storage(
        bucket_name, post_process_connection_path, updated_received_assets_connections
    )
    logger.info("Updated received json file is saved received_process_narrative.json")
    logger.info("DONE: get the updated received asset data")


async def process_narrative_post_processing(process_narrative_post_processing_args):
    """Process narrative post processing."""
    logger.info("INIT: Executing init functions of accuracy_csv")
    (
        bucket_name,
        connections_json_file_key,
        pnid_connections_json_path,
        post_process_connection_path,
        input_bounding_box_config_path,
    ) = process_narrative_post_processing_args
    received_assets_connections, _ = (
        await _load_config_and_necessary_variables(
            bucket_name, connections_json_file_key, pnid_connections_json_path
        )
    )
    await _get_updated_received_data(
        received_assets_connections,
        bucket_name,
        post_process_connection_path,
        input_bounding_box_config_path,
    )
    logger.info("DONE: init function of accuracy_csv is executed")
