"""This module consists of functions for data sheet accuracy"""

import json
import os
import pandas as pd
from src.local_execution.data_sheets.accuracy import property_value_accuracy
from src.local_execution.data_sheets.accuracy import property_name_accuracy
from src.utils.log import logger

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"


def load_config_and_necessary_variables():
    """Load config file and necessary variables for data sheet accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    ground_truth_folder_path = os.path.join(
        ROOT_FOLDER_PATH, config["ground_truth_data_sheet_folder_path"]
    )
    extracted_folder_path = os.path.join(
        ROOT_FOLDER_PATH, config["extracted_data_sheet_folder_path"]
    )
    data_sheet_accuracy_path = os.path.join(
        ROOT_FOLDER_PATH, config["data_sheet_accuracy_path"]
    )
    config["DATA_SHEET_ACCURACY_PATH"] = data_sheet_accuracy_path
    config["GROUND_TRUTH_FOLDER_PATH"] = ground_truth_folder_path
    config["EXTRACTED_FOLDER_PATH"] = extracted_folder_path
    logger.info("DONE: load_config_and_necessary_variables")
    return config


def process_for_all_equipment_accuracy(
    ground_truth_folder_path, extracted_folder_path, accuracy_function
):
    """Process for all equipment accuracy."""
    logger.info("INIT: Accuracy Matrix for all the Equipments")
    accuracy_matrix = []
    # ground_truth_folder_path = os.path.join(folder_path, "ground_truth")
    # extracted_folder_path = os.path.join(folder_path, "extracted")
    for equipment_name in os.listdir(ground_truth_folder_path):
        logger.info("Equipment name: %s", equipment_name)
        gt_equipment_path = os.path.join(ground_truth_folder_path, equipment_name)
        ext_equipment_path = os.path.join(extracted_folder_path, equipment_name)

        if os.path.isdir(gt_equipment_path) and os.path.isdir(ext_equipment_path):
            file_list = os.listdir(gt_equipment_path)
            accuracy_results = accuracy_function(
                file_list, equipment_name, gt_equipment_path, ext_equipment_path
            )
            accuracy_matrix += accuracy_results
    logger.info("DONE: Accuracy Matrix for all the Equipments completed.")
    return accuracy_matrix


def save_accuracy_results_to_csv(accuracy_results, file_path):
    """Save accuracy results to csv."""
    logger.info("INIT: Save accuracy results to csv")
    logger.info(file_path)
    accuracy_df = pd.DataFrame(accuracy_results)
    accuracy_df.to_csv(file_path, index=False)
    logger.info("DONE: Save accuracy results to csv")


def get_property_value_accuracy(
    data_sheet_accuracy_path, ground_truth_folder_path, extracted_folder_path
):
    """Get property value accuracy."""
    logger.info("INIT: Executing functions of property_value_accuracy")
    accuracy_matrix = process_for_all_equipment_accuracy(
        ground_truth_folder_path,
        extracted_folder_path,
        property_value_accuracy.get_accuracy,
    )
    property_value_accuracy_file_path = os.path.join(
        data_sheet_accuracy_path, "property_value_accuracy.csv"
    )
    save_accuracy_results_to_csv(accuracy_matrix, property_value_accuracy_file_path)
    logger.info("DONE: function of property_value_accuracy is executed")


def get_property_name_accuracy(
    accuracy_file_name,
    data_sheet_accuracy_path,
    ground_truth_folder_path,
    extracted_folder_path,
):
    """Get property name accuracy."""
    logger.info("INIT: Executing functions of property_name_accuracy")
    accuracy_matrix = process_for_all_equipment_accuracy(
        ground_truth_folder_path,
        extracted_folder_path,
        property_name_accuracy.assess_extraction_accuracy_for_equipment,
    )
    property_value_accuracy_file_path = os.path.join(
        data_sheet_accuracy_path, accuracy_file_name
    )
    save_accuracy_results_to_csv(accuracy_matrix, property_value_accuracy_file_path)
    logger.info("DONE: function of property_name_accuracy is executed")


def data_sheet_accuracy():
    """Data sheet accuracy."""
    config = load_config_and_necessary_variables()

    # ground_truth_folder_path = os.path.join(
    #     ROOT_FOLDER_PATH, "data/data_sheet/sanha/ground_truth"
    # )
    # extracted_folder_path = os.path.join(
    #     ROOT_FOLDER_PATH, f"data/data_sheet/sanha/{folder_name}"
    # )
    # data_sheet_accuracy_path = os.path.join(ROOT_FOLDER_PATH, "data/data_sheet/sanha")
    folder_name = "step1_step2_output_row"
    accuracy_file_name = f"{folder_name}_property_name_accuracy.csv"
    get_property_value_accuracy(
        config["DATA_SHEET_ACCURACY_PATH"],
        config["GROUND_TRUTH_FOLDER_PATH"],
        config["EXTRACTED_FOLDER_PATH"],
    )
    get_property_name_accuracy(
        accuracy_file_name,
        config["DATA_SHEET_ACCURACY_PATH"],
        config["GROUND_TRUTH_FOLDER_PATH"],
        config["EXTRACTED_FOLDER_PATH"],
    )


if __name__ == "__main__":
    data_sheet_accuracy()
