"""This module contains functions for connection accuracy"""

from src.utils.log import logger


def calculate_inlet_or_outlet_accuracy(
    expected_connections_count, received_connections_count, connection_type
):
    """This function calculates total asset connections(inlet or outlet) accuracy"""
    logger.info(f"INIT: calculate total {connection_type} accuracy")
    precision_total = 0
    recall_total = 0
    for asset_id in expected_connections_count:
        expected_connections = expected_connections_count[asset_id][connection_type]
        received_connections = received_connections_count[asset_id][connection_type]
        true_positives = min(expected_connections, received_connections)
        precision = 0
        recall = 0
        if received_connections != 0:
            precision = true_positives / received_connections
            if true_positives > received_connections:
                print("Not valid")
        if expected_connections != 0:
            recall = true_positives / expected_connections
        if expected_connections == 0 and received_connections == 0:
            precision = 1.0
            recall = 1.0

        precision_total += precision
        recall_total += recall

    num_assets = len(expected_connections_count)
    overall_precision = precision_total / num_assets
    overall_recall = recall_total / num_assets

    results = {
        "connection_count_precision": overall_precision,
        "connection_count_recall": overall_recall,
    }
    logger.info(
        f"DONE: calculating total {connection_type} accuracy and saved in json file."
    )
    return results


def calculate_inlet_and_outlet_accuracy(
    expected_connections_count, received_connections_count
):
    """This function calculates total asset connections(inlet and outlet) accuracy"""
    logger.info("INIT: calculate total asset connections(inlet and outlet) accuracy")
    precision_total = 0
    recall_total = 0

    for asset_id in expected_connections_count:
        expected_inlets = expected_connections_count[asset_id]["inlets"]
        expected_outlets = expected_connections_count[asset_id]["outlets"]
        expected_connections = expected_inlets + expected_outlets

        received_inlets = received_connections_count[asset_id]["inlets"]
        received_outlets = received_connections_count[asset_id]["outlets"]
        received_connections = received_inlets + received_outlets

        true_positives_inlets = min(expected_inlets, received_inlets)
        true_positives_outlets = min(expected_outlets, received_outlets)
        true_positives_connections = true_positives_inlets + true_positives_outlets

        precision = 0
        recall = 0

        if received_connections != 0:
            precision = true_positives_connections / received_connections
            if true_positives_connections > received_connections:
                print("Not valid")

        if expected_connections != 0:
            recall = true_positives_connections / expected_connections
        if expected_connections == 0 and received_connections == 0:
            precision = 1.0
            recall = 1.0
        precision_total += precision
        recall_total += recall

    num_assets = len(expected_connections_count)
    overall_precision_connections = precision_total / num_assets
    overall_recall_connections = recall_total / num_assets

    results = {
        "connection_count_precision": overall_precision_connections,
        "connection_count_recall": overall_recall_connections,
    }
    logger.info(
        f"""DONE: calculating total asset connections(inlet and outlet)
        accuracy for {num_assets} assets."""
    )
    return results


def calculate_inlet_and_outlet_asset_accuracy(
    expected_connections_count, received_connections_count
):
    """This function calculates asset-wise inlet and outlet connections accuracy"""
    logger.info("INIT: calculate asset-wise inlet and outlet connections accuracy")
    accuracy_dict = {}

    for asset_id in expected_connections_count:
        expected_inlets = expected_connections_count[asset_id]["inlets"]
        expected_outlets = expected_connections_count[asset_id]["outlets"]
        expected_connections = expected_inlets + expected_outlets

        received_inlets = received_connections_count[asset_id]["inlets"]
        received_outlets = received_connections_count[asset_id]["outlets"]
        received_connections = received_inlets + received_outlets

        true_positives_inlets = min(expected_inlets, received_inlets)
        true_positives_outlets = min(expected_outlets, received_outlets)
        true_positives_connections = true_positives_inlets + true_positives_outlets

        precision = 0
        recall = 0

        if received_connections != 0:
            precision = true_positives_connections / received_connections
            if true_positives_connections > received_connections:
                print("Not valid")

        if expected_connections != 0:
            recall = true_positives_connections / expected_connections
        if expected_connections == 0 and received_connections == 0:
            precision = 1.0
            recall = 1.0
        accuracy_dict[asset_id] = {
            "connection_count_precision": precision,
            "connection_count_recall": recall,
        }
    logger.info("DONE: calculating asset-wise inlet and outlet connections accuracy")
    return accuracy_dict


def calculate_inlet_or_outlet_asset_accuracy(
    expected_connections_count, received_connections_count, connection_type
):
    """This function calculates asset-wise inlet or outlet connections accuracy"""
    logger.info(f"INIT: calculate asset-wise {connection_type} accuracy")
    accuracy_results_dict = {}
    for asset_id in expected_connections_count:
        expected = expected_connections_count[asset_id][connection_type]
        received = received_connections_count[asset_id][connection_type]
        true_positives = min(expected, received)
        precision = 0
        recall = 0
        if received != 0:
            precision = true_positives / received
            if true_positives > received:
                print("Not valid")

        if expected != 0:
            recall = true_positives / expected
        if expected == 0 and received == 0:
            precision = 1.0
            recall = 1.0
        accuracy_results_dict[asset_id] = {
            "connection_count_precision": precision,
            "connection_count_recall": recall,
        }
    logger.info(
        f"Done: calculate asset-wise {connection_type} accuracy and saved in json file."
    )
    return accuracy_results_dict
