"""This module contains functions for control narrative accuracy"""

import os
import pandas as pd
from src.utils.log import logger


def write_control_loop_accuracy_to_csv(root_folder_path, config, control_loop_accuracy):
    """Write control loop accuracy"""
    logger.info("INIT: Saving control_loop accuracy metrics")
    csv_file_name = "control_loop_count_accuracy_metrics.csv"
    csv_file_path = os.path.join(
        root_folder_path, config["control_narrative_accuracy_path"], csv_file_name
    )
    df = pd.DataFrame.from_dict(control_loop_accuracy, orient="index")
    df_overall = df.loc[["overall_count_accuracy"]]
    df = df.drop(["overall_count_accuracy"])
    df.index = pd.to_numeric(df.index.str.extract(r"(\d+)")[0])
    df_sorted = df.sort_index()
    df_sorted.index = "narrative_" + df_sorted.index.astype(str)
    df_final = pd.concat([df_sorted, df_overall])
    df_final.to_csv(csv_file_path, index_label="narrative_id")
    logger.info(f"control_loop accuracy metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: control_loop accuracy metrics saved to CSV")


def write_instrument_accuracy_to_csv(root_folder_path, config, instrument_accuracy):
    """Write instrument accuracy"""
    logger.info("INIT: Saving instrument accuracy metrics")
    csv_file_name = "instrument_count_accuracy_metrics.csv"
    csv_file_path = os.path.join(
        root_folder_path, config["control_narrative_accuracy_path"], csv_file_name
    )
    df = pd.DataFrame.from_dict(instrument_accuracy, orient="index")
    df_overall = df.loc[["overall_count_accuracy"]]
    df = df.drop(["overall_count_accuracy"])
    df.index = pd.to_numeric(df.index.str.extract(r"(\d+)")[0])
    df_sorted = df.sort_index()
    df_sorted.index = "narrative_" + df_sorted.index.astype(str)
    df_final = pd.concat([df_sorted, df_overall])
    df_final.to_csv(csv_file_path, index_label="narrative_id")
    # df.to_csv(csv_file_path, index_label="narrative_id")
    logger.info(f"instrument accuracy metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: instrument accuracy metrics saved to CSV")


def write_control_loop_property_accuracy_to_csv(
    root_folder_path, config, property_accuracy, csv_file_name
):
    """Write control loop property accuracy"""
    logger.info("INIT: Saving property accuracy metrics")
    df = pd.DataFrame(property_accuracy)
    df.set_index("id", inplace=True)
    csv_file_path = os.path.join(
        root_folder_path, config["control_narrative_accuracy_path"], csv_file_name
    )
    df.to_csv(csv_file_path, index_label="id")
    logger.info(f"property accuracy metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: property accuracy metrics saved to CSV")


def write_business_control_loop_property_accuracy_to_csv(
    root_folder_path, config, property_accuracy, csv_file_name
):
    """Write control loop property accuracy"""
    logger.info("INIT: Saving property accuracy metrics")
    df = pd.DataFrame(property_accuracy)
    df.set_index("narrative_id", inplace=True)
    csv_file_path = os.path.join(
        root_folder_path, config["control_narrative_accuracy_path"], csv_file_name
    )
    df.to_csv(csv_file_path, index_label="narrative_id")
    logger.info(f"property accuracy metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: property accuracy metrics saved to CSV")


def write_instrument_property_accuracy_to_csv(
    root_folder_path, config, property_accuracy, csv_file_name
):
    """Write instrument property accuracy"""
    logger.info("INIT: Saving property accuracy metrics")
    # df = pd.DataFrame(property_accuracy)
    # df.set_index("narrative_id", inplace=True)
    csv_file_path = os.path.join(
        root_folder_path, config["control_narrative_accuracy_path"], csv_file_name
    )
    # df.to_csv(csv_file_path, index_label="narrative_id")
    df_metrics = pd.DataFrame.from_dict(property_accuracy, orient="index")
    df_metrics.to_csv(csv_file_path, index_label="narrative_id")
    logger.info(f"property accuracy metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: property accuracy metrics saved to CSV")


def save_to_csv(root_folder_path, config, accuracy, csv_file_name):
    """Save Accuracy matrix in CSV format"""
    logger.info("INIT: Saving property accuracy metrics")
    # csv_file_name = "instrument_count_accuracy_metrics.csv"
    csv_file_path = os.path.join(
        root_folder_path, config["control_narrative_accuracy_path"], csv_file_name
    )
    df = pd.DataFrame(accuracy)
    df.set_index(df.columns[0], inplace=True)
    df.to_csv(csv_file_path, index_label="narrative_id")
    logger.info(f"property accuracy metrics saved to CSV, {csv_file_path}")
    logger.info("DONE: property accuracy metrics saved to CSV")
