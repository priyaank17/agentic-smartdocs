"""This module provides functionality to generate accuracy csv"""

# pylint: disable=no-name-in-module
# pylint: disable=global-statement
# pylint: disable=invalid-name
import json
import os
from datetime import datetime
import pandas as pd
from src.utils.log import logger
from . import preprocessing as pr
from . import property_accuracy as property_ac
from . import connection_accuracy as connection_ac
from . import (
    all_properties_same_connection_accuracy as ap,
)

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"
config = None
expected_data = None
received_data = None
expected_connections_count = None
received_connections_count = None
expected_asset_csv = None


def load_config_and_necessary_variables():
    """This function loads the config and necessary variables."""
    logger.info("INIT: load_config_and_necessary_variables")
    global config
    global expected_data
    global received_data
    global expected_connections_count
    global received_connections_count
    global expected_asset_csv
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    expected_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["expected_asset_narrative_data_path"]
    )
    with open(expected_file_path, "r", encoding="utf-8") as f:
        expected_assets_connections = json.load(f)

    received_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["asset_narrative_data_path"]
    )
    with open(received_file_path, "r", encoding="utf-8") as f:
        received_assets_connections = json.load(f)
    expected_data, received_data = pr.get_asset_data(
        expected_assets_connections, received_assets_connections
    )
    expected_connections_count, received_connections_count = (
        pr.get_asset_connections_count(
            expected_assets_connections, received_assets_connections
        )
    )
    expected_asset_csv = os.path.join(ROOT_FOLDER_PATH, config["assets_table_csv_path"])
    logger.info("DONE: load_config_and_necessary_variables")


def get_property_accuracy():
    """This function returns the property accuracy metrics"""
    logger.info("INIT: Get property accuracy metrics functions")
    overall_property_accuracy = property_ac.calculate_total_asset_property_accuracy(
        expected_connections_count,
        received_data,
        expected_data,
        received_connections_count,
    )
    assetwise_property_accuracy = property_ac.calculate_asset_wise_property_accuracy(
        expected_connections_count,
        received_data,
        expected_data,
        received_connections_count,
    )
    assetwise_property_accuracy["overall_total_assets_accuracy"] = (
        overall_property_accuracy
    )
    logger.info("DONE: property accuracy metrics functions")
    return assetwise_property_accuracy


def write_property_accuracy_to_csv():
    """This function writes the property accuracy metrics to CSV"""
    logger.info("INIT: Saving property accuracy metrics")
    property_accuracy = get_property_accuracy()
    csv_file_name = "property_accuracy_metrics.csv"
    csv_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["accuracy_path"], csv_file_name
    )
    df = pd.DataFrame.from_dict(property_accuracy, orient="index")
    df.to_csv(csv_file_path, index_label="asset_name")
    logger.info(f"Property accuracy metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: Property accuracy metrics saved to CSV")


def get_connection_accuracy():
    """This function returns the connection accuracy metrics"""
    logger.info("INIT: Get connection accuracy metrics functions")
    overall_connection_accuracy = connection_ac.calculate_inlet_and_outlet_accuracy(
        expected_connections_count, received_connections_count
    )
    assetwise_connection_accuracy = (
        connection_ac.calculate_inlet_and_outlet_asset_accuracy(
            expected_connections_count, received_connections_count
        )
    )
    assetwise_connection_accuracy["overall_total_assets_accuracy"] = (
        overall_connection_accuracy
    )
    logger.info("DONE: connection accuracy metrics functions")
    return assetwise_connection_accuracy


def write_connection_accuracy_to_csv():
    """This function writes the connection accuracy metrics to CSV"""
    logger.info("INIT: Saving connection accuracy metrics")
    connection_accuracy = get_connection_accuracy()
    csv_file_name = "connection_accuracy_metrics.csv"
    csv_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["accuracy_path"], csv_file_name
    )
    df = pd.DataFrame.from_dict(connection_accuracy, orient="index")
    df.to_csv(csv_file_path, index_label="asset_name")
    logger.info(f"Connection accuracy metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: Connection accuracy metrics saved to CSV")


def get_all_properties_in_same_connection_accuracy():
    """This function returns the accuracy metrics having all properties in same connection"""
    logger.info(
        "INIT: Get accuracy metrics functions having all properties in same connection."
    )
    overall_all_property_accuracy = (
        ap.calculate_total_asset_all_properties_in_same_connection_accuracy(
            expected_connections_count,
            received_data,
            expected_data,
            received_connections_count,
        )
    )
    assetwise_property_accuracy = (
        ap.calculate_asset_wise_all_properties_in_same_connection_accuracy(
            expected_connections_count,
            received_data,
            expected_data,
            received_connections_count,
        )
    )
    assetwise_property_accuracy["overall_total_assets_accuracy"] = (
        overall_all_property_accuracy
    )
    logger.info(
        "DONE: accuracy metrics functions having all property in same connection."
    )
    return assetwise_property_accuracy


def write_asset_wise_all_properties_in_same_connection_accuracy_to_csv():
    """This function writes the accuracy metrics having all properties in same connection to CSV"""
    logger.info(
        "INIT: Saving accuracy metrics having all properties value in same connection."
    )
    all_property_accuracy = get_all_properties_in_same_connection_accuracy()
    csv_file_name = "all_properties_accuracy_metrics.csv"
    csv_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["accuracy_path"], csv_file_name
    )
    df = pd.DataFrame.from_dict(all_property_accuracy, orient="index")
    df.to_csv(csv_file_path, index_label="asset_name")
    logger.info(
        f"""the accuracy metrics having all properties
          value in same connection saved to CSV, {csv_file_path}"""
    )
    logger.info(
        "DONE: accuracy metrics having all properties value in same connection saved to CSV"
    )


def get_combine_accuracy_data(data1, data2):
    """This function combines the accuracy data"""
    logger.info("INIT: Combining the accuracy data.")
    combined_data = {}
    for asset_name, properties in data1.items():
        combined_data[asset_name] = properties.copy()
    for asset_name, properties in data2.items():
        if asset_name in combined_data:
            combined_data[asset_name].update(properties)
        else:
            combined_data[asset_name] = properties
    logger.info("DONE: Combined the accuracy data.")
    return combined_data


def generate_and_save_combined_accuracy_metrics():
    """This function generates and saves the combined accuracy metrics"""
    logger.info("INIT: Merging Property and Connection Accuracy Metrics")
    property_metrics = get_property_accuracy()
    connection_metrics = get_connection_accuracy()
    all_properties_in_same_connection_metrics = (
        get_all_properties_in_same_connection_accuracy()
    )
    combined_data_1 = get_combine_accuracy_data(property_metrics, connection_metrics)
    combined_data = get_combine_accuracy_data(
        combined_data_1, all_properties_in_same_connection_metrics
    )
    pr.round_accuracy_values(combined_data)
    current_date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    csv_file_name = f"process_narrative_accuracy_{current_date}.csv"
    csv_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["accuracy_path"], csv_file_name
    )
    combined_data_sorted = dict(
        sorted(
            combined_data.items(),
            key=lambda x: (
                float("inf")
                if x[0].startswith("overall_total_assets_accuracy")
                else float(x[0].split("_")[1])
            ),
        )
    )
    df = pd.DataFrame.from_dict(combined_data_sorted, orient="index")
    df.to_csv(csv_file_path, index_label="asset_name")
    logger.info(f"Combined Accuracy Metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: Combined Accuracy Metrics saved to CSV")


def init():
    """This function executes the init functions of accuracy_csv"""
    logger.info("INIT: Executing init functions of accuracy_csv")
    load_config_and_necessary_variables()
    # write_connection_accuracy_to_csv()
    # write_property_accuracy_to_csv()
    generate_and_save_combined_accuracy_metrics()
    # write_asset_wise_all_properties_in_same_connection_accuracy_to_csv()
    logger.info("DONE: init function of accuracy_csv is executed")


if __name__ == "__main__":
    init()
