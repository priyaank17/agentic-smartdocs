"""This module calculates the accuracy of control narrative"""

import json
import os

# from datetime import datetime
from src.local_execution.control_narrative.accuracy import (
    control_loop_count_accuracy as control_loop_count_ac,
)
from src.local_execution.control_narrative.accuracy import (
    instrument_count_accuracy as instrument_count_ac,
)
from src.local_execution.control_narrative.accuracy import preprocessing as pr
from src.local_execution.control_narrative.accuracy import (
    control_loop_property_accuracy as control_loop_property_ac,
)
from src.local_execution.control_narrative.accuracy import (
    instrument_property_accuracy as instrument_property_ac,
)
from src.local_execution.control_narrative.accuracy import (
    control_loop_overall_property_accuracy as cl_overall_property_ac,
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
    overall_control_loop_count = (
        control_loop_count_ac.calculate_total_control_loop_count_accuracy(
            config["EXPECTED_CONTROL_LOOP_COUNT"], config["RECEIVED_CONTROL_LOOP_COUNT"]
        )
    )
    control_loop_count_accuracy["overall_count_accuracy"] = overall_control_loop_count
    logger.info("DONE: calculated control_loop_count_accuracy")
    return control_loop_count_accuracy


def calculate_instrument_count_accuracy(config):
    """Calculates the accuracy of instrument count"""
    logger.info("INIT: calculate_instrument_count_accuracy")
    instrument_count_accuracy = instrument_count_ac.calculate_instrument_count_accuracy(
        config["EXPECTED_INSTRUMENT_COUNT"], config["RECEIVED_INSTRUMENT_COUNT"]
    )
    overall_instrument_count = (
        instrument_count_ac.calculate_total_instrument_count_accuracy(
            config["EXPECTED_INSTRUMENT_COUNT"], config["RECEIVED_INSTRUMENT_COUNT"]
        )
    )
    instrument_count_accuracy["overall_count_accuracy"] = overall_instrument_count
    logger.info("DONE: calculated instrument_count_accuracy")
    return instrument_count_accuracy


def accuracy_control_narrative(config):
    """This function executes the init functions of accuracy_csv"""
    logger.info("INIT: Executing init functions of accuracy_csv")
    control_loop_accuracy = calculate_control_loop_count_accuracy(config)
    instrument_accuracy = calculate_instrument_count_accuracy(config)
    ut.write_control_loop_accuracy_to_csv(
        ROOT_FOLDER_PATH, config, control_loop_accuracy
    )
    ut.write_instrument_accuracy_to_csv(
        ROOT_FOLDER_PATH, config, instrument_accuracy
    )
    process_variable_accuracy = control_loop_property_ac.process_variable_accuracy(
        config["EXPECTED_CONTROL_LOOP_DATA"], config["RECEIVED_CONTROL_LOOP_DATA"]
    )
    controller_accuracy = control_loop_property_ac.controller_accuracy(
        config["EXPECTED_CONTROL_LOOP_DATA"], config["RECEIVED_CONTROL_LOOP_DATA"]
    )
    final_control_element_accuracy = (
        control_loop_property_ac.final_control_element_accuracy(
            config["EXPECTED_CONTROL_LOOP_DATA"], config["RECEIVED_CONTROL_LOOP_DATA"]
        )
    )
    ut.write_control_loop_property_accuracy_to_csv(
        ROOT_FOLDER_PATH,
        config,
        process_variable_accuracy,
        "pr_process_variable_accuracy_metrics.csv",
    )
    ut.write_control_loop_property_accuracy_to_csv(
        ROOT_FOLDER_PATH,
        config,
        controller_accuracy,
        "pr_controller_accuracy_metrics.csv",
    )
    ut.write_control_loop_property_accuracy_to_csv(
        ROOT_FOLDER_PATH,
        config,
        final_control_element_accuracy,
        "pr_final_control_element_accuracy_metrics.csv",
    )
    overall_control_loop_property_accuracy = (
        control_loop_property_ac.overall_property_accuracy(
            process_variable_accuracy,
            controller_accuracy,
            final_control_element_accuracy,
        )
    )
    ut.write_control_loop_property_accuracy_to_csv(
        ROOT_FOLDER_PATH,
        config,
        overall_control_loop_property_accuracy,
        "control_loop_property_accuracy_metrics.csv",
    )
    instrument_property_accuracy = instrument_property_ac.instrument_property_accuracy(
        config["EXPECTED_INSTRUMENT_DATA"], config["RECEIVED_INSTRUMENT_DATA"]
    )
    ut.write_instrument_property_accuracy_to_csv(
        ROOT_FOLDER_PATH,
        config,
        instrument_property_accuracy,
        "instrument_property_accuracy_metrics.csv",
    )
    all_control_loop_property = cl_overall_property_ac.calculate_accuracy_per_property(
        config["EXPECTED_CONTROL_LOOP_DATA"], config["RECEIVED_CONTROL_LOOP_DATA"]
    )
    ut.write_instrument_property_accuracy_to_csv(
        ROOT_FOLDER_PATH,
        config,
        all_control_loop_property,
        "overall_control_loop_accuracy_metrics.csv",
    )
    logger.info("DONE: init function of accuracy_csv is executed")


if __name__ == "__main__":
    CONFIG = load_config_and_necessary_variables()
    accuracy_control_narrative(CONFIG)
