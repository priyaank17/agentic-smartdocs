"""This module consists of functions for Property Name Accuracy."""

import os
import pandas as pd
from src.utils.log import logger
from src.data_sheets.constant import (
    standard_property_name_list_path,
    split_alternate_names,
    get_specific_standard_df,
    update_ground_truth_extracted_standard_property_name,
    get_standard_property_df,
)


def load_csv(csv_file):
    """Load CSV file into a DataFrame.
    The processing includes dropping rows with missing property names,
    stripping leading and trailing spaces from the property names,
    and treating the column names as property names
    if the specified column does not exist."""
    df = pd.read_csv(csv_file)
    if "standard_property_name" in df.columns:
        property_names_df = df[["standard_property_name"]].dropna(
            subset=["standard_property_name"]
        )
        property_names_df["standard_property_name"] = property_names_df[
            "standard_property_name"
        ].str.strip()
    else:
        property_names_df = pd.DataFrame({"standard_property_name": df.columns})
    return property_names_df


def calculate_precision_recall(
    equipment_name,
    table_name,
    ground_truth_df,
    extracted_df,
    total_standard_properties_count,
):
    """Calculate precision and recall."""
    correct_count = len(
        set(ground_truth_df["standard_property_name"]).intersection(
            set(extracted_df["standard_property_name"])
        )
    )
    missed_count = len(
        set(ground_truth_df["standard_property_name"])
        - set(extracted_df["standard_property_name"])
    )
    extra_count = len(
        set(extracted_df["standard_property_name"])
        - set(ground_truth_df["standard_property_name"])
    )

    precision = (
        correct_count / (correct_count + extra_count)
        if (correct_count + extra_count) > 0
        else 0
    )
    recall = (
        correct_count / (correct_count + missed_count)
        if (correct_count + missed_count) > 0
        else 0
    )

    accuracy_dict = {
        "equipment_name": equipment_name,
        "table_name": table_name,
        "total properties": total_standard_properties_count,
        "total_extracted": len(set(extracted_df["standard_property_name"])),
        "total_correctly_extracted_property_name": correct_count,
        "total expected": len(set(ground_truth_df["standard_property_name"])),
        # "total_false_positive_property_names": extra_count,
        # "total_missed_property_names": missed_count,
        "precision": precision,
        "recall": recall,
    }
    return accuracy_dict


def get_property_name_accuracy(
    equipment_name,
    table_name,
    ground_truth_property_names_df,
    extracted_property_names_df,
    total_standard_properties_count,
):
    """Get property name accuracy."""
    accuracy_dict = calculate_precision_recall(
        equipment_name,
        table_name,
        ground_truth_property_names_df,
        extracted_property_names_df,
        total_standard_properties_count,
    )
    return accuracy_dict


def get_csv_files(file_name, ground_truth_folder_path, extracted_folder_path):
    """Get CSV files."""
    ground_truth_csv_file = os.path.join(ground_truth_folder_path, file_name)
    extracted_csv_file = os.path.join(extracted_folder_path, file_name)
    return ground_truth_csv_file, extracted_csv_file


def assess_extraction_accuracy_for_equipment(
    file_list, equipment_name, ground_truth_folder_path, extracted_folder_path
):
    """Assess extraction accuracy for equipment."""
    accuracy_results = []
    for file_name in file_list:
        if file_name.endswith(".csv"):
            ground_truth_csv_file, extracted_csv_file = get_csv_files(
                file_name, ground_truth_folder_path, extracted_folder_path
            )
            if os.path.exists(extracted_csv_file):
                ground_truth_property_names_df = load_csv(ground_truth_csv_file)
                extracted_property_names_df = load_csv(extracted_csv_file)
                (
                    ground_truth_filtered_property_names_df,
                    extracted_filtered_property_names_df,
                ) = update_ground_truth_extracted_standard_property_name(
                    equipment_name,
                    ground_truth_property_names_df,
                    extracted_property_names_df,
                )
                accuracy_dict = get_accuracy(
                    file_name,
                    equipment_name,
                    ground_truth_filtered_property_names_df,
                    extracted_filtered_property_names_df,
                )
                accuracy_results.append(accuracy_dict)
                logger.info(f"Accuracy Matrix for {file_name} completed.")
            else:
                logger.info(f"Extracted data for {file_name} does not exist.")
    return accuracy_results


def get_accuracy(
    file_name,
    equipment_name,
    ground_truth_property_names_df,
    extracted_property_names_df,
):
    """Calculates the accuracy of the extracted property names based on the ground truth data."""
    table_name = file_name.split(".")[0]
    chevron_asset_class_tag = equipment_name.split("_")[0].upper()
    total_standard_properties_count = len(
        get_all_standard_property(
            standard_property_name_list_path, chevron_asset_class_tag, table_name
        )
    )
    accuracy_dict = get_property_name_accuracy(
        equipment_name,
        table_name,
        ground_truth_property_names_df,
        extracted_property_names_df,
        total_standard_properties_count,
    )
    return accuracy_dict


def combine_standard_property_names(df, columns):
    """Combine standard property names from a DataFrame."""
    melted_df = df.melt(value_vars=columns, value_name="property_name")
    melted_df = melted_df.dropna(subset=["property_name"])
    melted_df = melted_df[melted_df["property_name"] != ""]
    return melted_df["property_name"].unique().tolist()


def get_all_standard_property(
    property_name_list_path, chevron_asset_class_tag, table_name
):
    """Get all standard property names for a table."""
    property_name_df = get_standard_property_df(property_name_list_path)
    asset_class = property_name_df.loc[
        property_name_df["chevron_asset_class_tag"].str.contains(
            chevron_asset_class_tag, na=False
        ),
        "asset_class",
    ].iloc[0]
    property_name_df = get_specific_standard_df(property_name_df, asset_class)
    possible_table_columns = [
        col for col in property_name_df.columns if col.startswith("possible_table_")
    ]
    filtered_df = property_name_df[
        property_name_df[possible_table_columns].eq(table_name).any(axis=1)
    ]
    filtered_df = split_alternate_names(filtered_df)
    columns_to_extract = [
        column
        for column in filtered_df.columns
        if column.startswith("alternate_name") or column == "standard_property_name"
    ]
    standard_property_names_list = combine_standard_property_names(
        filtered_df, columns_to_extract
    )
    return standard_property_names_list
