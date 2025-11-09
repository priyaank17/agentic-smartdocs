"""This module calculates the accuracy of control narrative"""

import json
import os

# from datetime import datetime
from src.local_execution.control_narrative.business_accuracy_matrix import (
    control_loop_count_accuracy as control_loop_count_ac,
)
from src.local_execution.control_narrative.business_accuracy_matrix import (
    instrument_count_accuracy as instrument_count_ac,
)
from src.local_execution.control_narrative.accuracy import preprocessing as pr
from src.local_execution.control_narrative.business_accuracy_matrix import (
    instrument_property_accuracy as instrument_property_ac,
)
from src.local_execution.control_narrative.business_accuracy_matrix import (
    control_loop_property_accuracy as control_loop_property_ac,
)
from src.utils.log import logger
from src.local_execution.control_narrative.accuracy import utils as ut

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"


def load_config_and_necessary_variables():
    """Load config file and necessary variables for control narrative accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    expected_control_loop_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["expected_control_loop_data_path"]
    )
    with open(expected_control_loop_file_path, "r", encoding="utf-8") as f:
        expected_control_loop_data = json.load(f)

    received_control_loop_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["extracted_control_loop_path"]
    )
    with open(received_control_loop_file_path, "r", encoding="utf-8") as f:
        received_control_loop_data = json.load(f)
    expected_control_loop_count, received_control_loop_count = (
        pr.get_control_loops_count(
            expected_control_loop_data, received_control_loop_data
        )
    )

    expected_instrument_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["expected_instrument_data_path"]
    )
    with open(expected_instrument_file_path, "r", encoding="utf-8") as f:
        expected_instrument_data = json.load(f)
    received_instrument_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["extracted_instrument_data_path"]
    )
    with open(received_instrument_file_path, "r", encoding="utf-8") as f:
        received_instrument_data = json.load(f)
    expected_instrument_count, received_instrument_count = pr.get_instruments_count(
        expected_instrument_data, received_instrument_data
    )

    config["EXPECTED_CONTROL_LOOP_DATA"] = expected_control_loop_data
    config["RECEIVED_CONTROL_LOOP_DATA"] = received_control_loop_data
    config["EXPECTED_CONTROL_LOOP_COUNT"] = expected_control_loop_count
    config["RECEIVED_CONTROL_LOOP_COUNT"] = received_control_loop_count
    config["EXPECTED_INSTRUMENT_DATA"] = expected_instrument_data
    config["RECEIVED_INSTRUMENT_DATA"] = received_instrument_data
    config["EXPECTED_INSTRUMENT_COUNT"] = expected_instrument_count
    config["RECEIVED_INSTRUMENT_COUNT"] = received_instrument_count
    logger.info("DONE: load_config_and_necessary_variables")
    return config


def calculate_control_loop_count_accuracy(config):
    """Calculates the accuracy of control loop count"""
    logger.info("INIT: calculate_control_loop_count_accuracy")
    control_loop_count_accuracy = (
        control_loop_count_ac.calculate_control_loop_count_accuracy(
            config["EXPECTED_CONTROL_LOOP_COUNT"], config["RECEIVED_CONTROL_LOOP_COUNT"]
        )
    )
    logger.info("DONE: calculated control_loop_count_accuracy")
    return control_loop_count_accuracy


def calculate_instrument_count_accuracy(config):
    """Calculates the accuracy of instrument count"""
    logger.info("INIT: calculate_instrument_count_accuracy")
    instrument_count_accuracy = instrument_count_ac.calculate_instrument_count_accuracy(
        config["EXPECTED_INSTRUMENT_COUNT"], config["RECEIVED_INSTRUMENT_COUNT"]
    )
    logger.info("DONE: calculated instrument_count_accuracy")
    return instrument_count_accuracy


def accuracy_control_loop_business(config):
    """This function executes the init functions of accuracy_csv"""
    logger.info("INIT: Executing init functions of accuracy_csv")
    control_loop_count_accuracy = calculate_control_loop_count_accuracy(config)
    ut.save_to_csv(
        ROOT_FOLDER_PATH,
        config,
        control_loop_count_accuracy,
        "control_loop_count_accuracy_metrics.csv",
    )
    control_loop_property_accuracy = (
        control_loop_property_ac.control_loop_property_accuracy(
            config["EXPECTED_CONTROL_LOOP_DATA"], config["RECEIVED_CONTROL_LOOP_DATA"]
        )
    )
    ut.write_business_control_loop_property_accuracy_to_csv(
        ROOT_FOLDER_PATH,
        config,
        control_loop_property_accuracy,
        "control_loop_property_accuracy_metrics.csv",
    )
    logger.info("DONE: init function of accuracy_csv is executed")


def accuracy_instrument_business(config):
    """This function executes the init functions of accuracy_csv"""
    instrument_count_accuracy = calculate_instrument_count_accuracy(config)
    ut.save_to_csv(
        ROOT_FOLDER_PATH,
        config,
        instrument_count_accuracy,
        "instrument_count_accuracy_metrics.csv",
    )
    instrument_property_accuracy = instrument_property_ac.instrument_property_accuracy(
        config["EXPECTED_INSTRUMENT_DATA"], config["RECEIVED_INSTRUMENT_DATA"]
    )
    ut.save_to_csv(
        ROOT_FOLDER_PATH,
        config,
        instrument_property_accuracy,
        "instrument_property_accuracy_metrics.csv",
    )
    # ut.write_instrument_property_accuracy_to_csv(
    #     ROOT_FOLDER_PATH,
    #     config,
    #     instrument_property_accuracy,
    #     "instrument_property_accuracy_metrics.csv",
    # )


if __name__ == "__main__":
    CONFIG = load_config_and_necessary_variables()
    accuracy_instrument_business(CONFIG)
    accuracy_control_loop_business(CONFIG)
