"""This module contains functions to calculate the accuracy of extracted property values."""

import os
import pandas as pd
from src.utils.log import logger
from src.data_sheets.constant import (
    update_ground_truth_extracted_standard_property_name
)


def load_csv(file_path):
    """Loads a CSV file and"""
    df = pd.read_csv(file_path, dtype=str)
    return df


def filter_df(data, drop_columns=None):
    """returns a dictionary of property names
    and their corresponding values."""
    if drop_columns is None:
        drop_columns = []
    if "standard_property_name" in data.columns:
        duplicate_rows = data[
            data.duplicated(subset=["standard_property_name"], keep=False)
        ]
        if not duplicate_rows.empty:
            logger.info("Duplicate entries found:")
            logger.info(duplicate_rows)

        # Drop duplicate entries based on 'standard_property_name' column
        data = data.drop_duplicates(subset=["standard_property_name"])
        data = data.set_index(
            "standard_property_name"
        )  # Set 'standard_property_name' column as index
    else:
        # If 'standard_property_name' column is not present, set the first column as index
        data = data.set_index(data.columns[0])
        message = "'standard_property_name' column not found. "
        message += f"Setting first column '{data.index.name}' as index."
        logger.info(message)
    data.replace("", float("nan"), inplace=True)
    data.fillna("", inplace=True)
    data = data.drop(columns=drop_columns, errors="ignore")
    data_dict = data.to_dict(orient="index")
    return data_dict


def calculate_accuracy(equipment_name, table_name, extracted_data, ground_truth):
    """Calculates the accuracy of the extracted property values based on the ground truth data."""
    accuracy_results = []
    accuracy_dic = {}
    for standard_property_name, extracted_row in extracted_data.items():
        if standard_property_name in ground_truth:
            ground_truth_row = ground_truth[standard_property_name]
            total_extracted_properties = len(extracted_row)
            correct_count = 0
            for key, value in extracted_row.items():
                if key in ground_truth_row and value == ground_truth_row[key]:
                    correct_count += 1
            accuracy_dic = {
                "equipment_name": equipment_name,
                "table_name": table_name,
                "standard_property_name": standard_property_name,
                "total_extracted_value": total_extracted_properties,
                "total_ground_truth_value": len(ground_truth_row),
                "correct_property_value": correct_count,
                "hallucinated_property_value": total_extracted_properties
                - correct_count,
                "not_extracted_property_value": len(ground_truth_row) - correct_count,
                "accuracy": (correct_count / total_extracted_properties),
            }
            # else:
            #     accuracy_dic = {
            #         "table_name": table_name,
            #         "standard_property_name": standard_property_name,
            #         "total_extracted_value": "NA",
            #         "total_ground_truth_value": "NA",
            #         "correct_property_value": "NA",
            #         "hallucinated_property_value": "NA",
            #         "not_extracted_property_value": "NA",
            #         "accuracy": 0
            #     }
            accuracy_results.append(accuracy_dic)
    return accuracy_results


def get_accuracy(
    file_list, equipment_name, ground_truth_folder_path, extracted_folder_path
):
    """Calculates the accuracy of the extracted property values based on the ground truth data."""
    accuracy_final = []
    # accuracy_results = []
    for file_name in file_list:
        if file_name.endswith(".csv"):
            ground_truth_csv_file = os.path.join(ground_truth_folder_path, file_name)
            extracted_csv_file = os.path.join(extracted_folder_path, file_name)
            if os.path.exists(extracted_csv_file):
                table_name = file_name.split(".")[0]
                skip_table = ["nozzle", "nozzles", "heat_curves", "heat_curve"]
                if table_name not in skip_table:
                    logger.info(f"Getting Accuracy Matrix for {table_name}")
                    columns_to_drop = ["property_name", "units"]
                    extracted_df = load_csv(extracted_csv_file)
                    ground_truth_df = load_csv(ground_truth_csv_file)

                    ground_truth_filtered_df, extracted_filtered_df = (
                        update_ground_truth_extracted_standard_property_name(
                            equipment_name,
                            ground_truth_df,
                            extracted_df,
                        )
                    )
                    extracted_filtered_df = filter_df(
                        extracted_filtered_df, drop_columns=["property_name"]
                    )
                    ground_truth_filtered_df = filter_df(
                        ground_truth_filtered_df, drop_columns=columns_to_drop
                    )
                    accuracy_dict = calculate_accuracy(
                        equipment_name, table_name, extracted_filtered_df, ground_truth_filtered_df
                    )
                    accuracy_final = accuracy_final + accuracy_dict
                    logger.info(f"Accuracy Matrix for {table_name} completed.")
                    # accuracy_results.append(accuracy_dict)
            else:
                logger.info(f"Extracted data for {file_name} does not exist.")
    return accuracy_final
