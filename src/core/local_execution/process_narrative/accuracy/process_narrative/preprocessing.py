"""This module contains functions for preprocessing"""

from src.utils.log import logger


def get_asset_data(expected_assets_connections, received_assets_connections):
    """This function returns the asset data of both generated and received file"""
    logger.info("INIT: Get asset data of both generated and received file.")
    expected_data = {}
    for item in expected_assets_connections:
        asset_id = item["asset_id"]
        if asset_id not in expected_data:
            expected_data[asset_id] = []
        expected_data[asset_id].append(item)
    received_data = {}
    for item in received_assets_connections:
        asset_id = item["asset_id"]
        if asset_id not in received_data:
            received_data[asset_id] = []
        received_data[asset_id].append(item)

    common_asset_ids = set(expected_data.keys()) & set(received_data.keys())
    print(common_asset_ids)
    expected_data_common = {
        asset_id: expected_data[asset_id] for asset_id in common_asset_ids
    }
    received_data_common = {
        asset_id: received_data[asset_id] for asset_id in common_asset_ids
    }
    logger.info("DONE: Got asset data of both generated and received file.")
    return expected_data_common, received_data_common


def calculate_expected_connections_count(expected_assets_connections):
    """This function calculates the expected connections count"""
    logger.info("INIT: calculate expected connections count")
    expected_connections_count = {}
    for connection in expected_assets_connections:
        asset_id = connection.get("asset_id")
        connection_type = connection.get("connection_type")
        # connection_in_narrative = connection.get(
        #     "is_connection_type_mentioned_in_narrative"
        # )
        if (
            asset_id is not None
            and connection_type is not None
            # and connection_in_narrative is True
        ):
            asset_summary = expected_connections_count.get(
                asset_id, {"inlets": 0, "outlets": 0}
            )
            if connection_type == "IN_LET":
                asset_summary["inlets"] += 1
            elif connection_type == "OUT_LET":
                asset_summary["outlets"] += 1
            expected_connections_count[asset_id] = asset_summary

    logger.info("DONE: calculated expected connections count")
    return expected_connections_count


def calculate_received_connections_count(received_assets_connections):
    """This function calculates the received connections count"""
    logger.info("INIT: calculate received connections count")
    received_connections_count = {}
    for connection in received_assets_connections:
        asset_id = connection.get("asset_id")
        connection_type = connection.get("connection_type")
        if asset_id is not None and connection_type is not None:
            asset_summary = received_connections_count.get(
                asset_id, {"inlets": 0, "outlets": 0}
            )
            if connection_type == "IN_LET":
                asset_summary["inlets"] += 1
            elif connection_type == "OUT_LET":
                asset_summary["outlets"] += 1
            received_connections_count[asset_id] = asset_summary

    logger.info("DONE: calculated received connections count")
    return received_connections_count


def align_connection_counts(expected_connections_count, received_connections_count):
    """This function aligns the connection counts"""
    common_keys = set(expected_connections_count.keys()) & set(
        received_connections_count.keys()
    )
    aligned_expected_count = {
        key: expected_connections_count[key] for key in common_keys
    }
    aligned_received_count = {
        key: received_connections_count[key] for key in common_keys
    }
    return aligned_expected_count, aligned_received_count


def get_asset_connections_count(
    expected_assets_connections, received_assets_connections
):
    """This function returns the asset connections count"""
    logger.info("INIT: Get assets connections(inlet and outlet) count")
    expected_connections_count = calculate_expected_connections_count(
        expected_assets_connections
    )
    received_connections_count = calculate_received_connections_count(
        received_assets_connections
    )
    print("expected_connections_count ", expected_connections_count)
    print("received_connections_count ", received_connections_count)
    aligned_expected_count, aligned_received_count = align_connection_counts(
        expected_connections_count, received_connections_count
    )
    logger.info("DONE: counted assets connections(inlet and outlet)")
    # return expected_connections_count, received_connections_count
    return aligned_expected_count, aligned_received_count


def round_accuracy_values(accuracy_metrics):
    """This function rounds the accuracy values"""
    logger.info("INIT: round_accuracy_values")
    for asset_name, properties in accuracy_metrics.items():
        for key, value in properties.items():
            if isinstance(value, float):
                accuracy_metrics[asset_name][key] = round(value, 3)
    logger.info("DONE: round_accuracy_values")
