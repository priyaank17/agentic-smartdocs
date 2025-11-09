"""This module contains functions for all properties in same connection accuracy"""

from src.utils.log import logger


def map_all_properties_in_same_connection(
    received_data, expected_data, received_asset_id, expected_asset_id
):
    """This function maps all properties in same connection"""
    logger.info(f"INIT: map  {received_asset_id} and {expected_asset_id}")
    properties = {}
    received_connections = received_data.get(received_asset_id, {})
    logger.info("received_connections.")
    expected_connections = expected_data.get(expected_asset_id, {})
    used_received_id = set()
    logger.info("set used_received_id.")
    used_expected_id = set()
    logger.info("set used_expected_id.")
    for p_connection in received_connections:
        for a_connection in expected_connections:
            a = (
                p_connection["connection_type"].lower()
                == a_connection["connection_type"].lower()
                and p_connection.get("source_asset_name", "").lower()
                == a_connection.get("source_asset_name", "").lower()
                and p_connection.get("destination_asset_name", "").lower()
                == a_connection.get("destination_asset_name", "").lower()
                and p_connection["pressure"]["value"]
                == a_connection["pressure"]["value"]
                and p_connection["temperature"]["value"]
                == a_connection["temperature"]["value"]
                and p_connection["flow_rate"]["value"]
                == a_connection["flowrate"]["value"]
                # and a_connection.get("is_connection_type_mentioned_in_narrative") is True
                and p_connection["id"] not in used_received_id
                and a_connection["id"] not in used_expected_id
            )
            if a:
                properties[p_connection["id"]] = a_connection["id"]
                used_received_id.add(p_connection["id"])
                used_expected_id.add(a_connection["id"])
                break
    logger.info(f"DONE: mapped {received_asset_id} and {expected_asset_id}")
    return properties


def compute_accuracy(
    best_connections, received_connections_count, expected_connections_count, ast_id
):
    """This function computes accuracy"""
    logger.info(f"INIT: compute accuracy of {ast_id}")
    true_positive = len(best_connections)
    logger.info(f"true_positive: {true_positive}")
    received_total = (
        received_connections_count[ast_id]["inlets"]
        + received_connections_count[ast_id]["outlets"]
    )
    logger.info(f"received_total: {received_total}")
    expected_total = (
        expected_connections_count[ast_id]["inlets"]
        + expected_connections_count[ast_id]["outlets"]
    )
    logger.info(f"expected_total: {expected_total}")
    accuracy = None
    if expected_total == 0 and received_total == 0:
        accuracy = 1.0
        logger.info(f"accuracy: {accuracy}")
    elif received_total == 0:
        accuracy = 0.0
        logger.info(f"accuracy: {accuracy}")
    else:
        accuracy = true_positive / received_total
    logger.info(f"DONE: accuracy of {ast_id},{accuracy} ")
    return accuracy


def calculate_asset_wise_all_properties_in_same_connection_accuracy(
    expected_connections_count, received_data, expected_data, received_connections_count
):
    """This function calculates asset-wise property accuracy"""
    logger.info("INIT: calculate asset-wise property accuracy")
    all_property_accuracy_dict = {}

    for ast_id in expected_connections_count.keys():
        all_property_accuracy = compute_accuracy(
            map_all_properties_in_same_connection(
                received_data, expected_data, ast_id, ast_id
            ),
            received_connections_count,
            expected_connections_count,
            ast_id,
        )
        all_property_accuracy_dict[ast_id] = {
            "all_properties_accuracy": all_property_accuracy,
        }
    logger.info("DONE: calculating asset-wise property accuracy")
    return all_property_accuracy_dict


def calculate_total_asset_all_properties_in_same_connection_accuracy(
    expected_connections_count, received_data, expected_data, received_connections_count
):
    """This function calculates total asset-wise property accuracy"""
    logger.info("INIT: calculate total_asset_property_accuracy")
    total_accuracy = 0
    num_assets = len(expected_connections_count)
    for ast_name in expected_connections_count.keys():
        all_property_accuracy = compute_accuracy(
            map_all_properties_in_same_connection(
                received_data, expected_data, ast_name, ast_name
            ),
            received_connections_count,
            expected_connections_count,
            ast_name,
        )
        total_accuracy += all_property_accuracy
    asset_accuracy = {
        "all_properties_accuracy": total_accuracy / num_assets if num_assets > 0 else 0
    }
    logger.info("DONE: calculating total_asset_property_accuracy")
    return asset_accuracy
