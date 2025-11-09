"""
This module defines constants used throughout the application.
It includes table names and columns to be dropped for specific tables.
"""

import os
import pandas as pd
from src.utils.log import logger
from src.utils.s3_download_upload import read_csv_from_storage

table_name = [
    "description",
    "performance_of_one_unit",
    "nozzle",
    "performance_data",
    "operating_conditions",
    "design_and_construction",
    "maximum_loading_case",
    "minimum_loading_case_at_a1",
    "minimum_loading_case_at_a2",
    "minimum_loading_case_at_a3",
    "general",
    "construction",
    "liquid",
    "motor_driver",
    "process_data",
    "construction_data_per_core",
    "design",
    "fin_data",
]

drop_columns_performance_of_unit = ["units", "artisan_name", "Unnamed: 0"]

drop_columns_construction = ["units", "artisan_name", "Unnamed: 0"]

drop_columns_table_format_2_data = ["units", "artisan_name", "Unnamed: 0"]

drop_columns_nozzle = ["Unnamed: 0"]

columns_cba_operating_conditions = [
    "standard_property_name",
    "property_name",
    "late_case_expander",
    "late_case_recompressor",
]

columns_operating_conditions = ["standard_property_name", "property_name", "value"]

columns_performance_table = ["standard_property_name", "property_name", "value"]

columns_design_and_construction = ["standard_property_name", "property_name", "value"]

columns_maximum_loading_case = ["standard_property_name", "property_name", "case_1"]

columns_minimum_loading_case = ["standard_property_name", "property_name", "case_1"]

columns_design_data = ["standard_property_name", "property_name", "value"]

columns_general = ["standard_property_name", "property_name", "value"]

columns_description = ["standard_property_name", "property_name", "value"]

standard_property_name_list_path = os.path.join(
    "src", "constants", "previous_standard_name.csv"
)

columns_table_format_1_data = ["standard_property_name", "property_name", "value"]


def get_standard_property_df(property_name_list_path):
    """Load property names from a CSV file and return as a DataFrame."""
    logger.info(f"Attempting to load property names from: {property_name_list_path}")
    if not os.path.exists(property_name_list_path):
        logger.error(f"File not found: {property_name_list_path}")
        return []

    try:
        property_name_df = pd.read_csv(property_name_list_path)
    except FileNotFoundError as e:
        logger.error(f"Error reading file: {e}")
        return []
    return property_name_df


def get_specific_standard_df(combined_df, asset_class):
    """Get a DataFrame that only contains rows with a specific asset class."""
    combined_df = combined_df.fillna("")
    df = combined_df[combined_df["asset_class"].str.contains(asset_class)]
    return df


def split_alternate_names(df):
    """Split alternate names into separate columns."""
    split_df = df["alternate_names"].str.split(",", expand=True)
    for i in range(split_df.shape[1]):
        split_df.rename(columns={i: f"alternate_name_{i}"}, inplace=True)
    df = pd.concat([df, split_df], axis=1)
    df.drop(columns=["alternate_names"], inplace=True)
    return df


def update_standard_property_names(standard_df, output_df):
    """Update standard property names and by matching it with alternate
    names and standard property names to get the exact accuracy result"""
    standard_df["alternate_names"] = standard_df["alternate_names"].fillna("")
    standard_df = split_alternate_names(standard_df)
    for index, row in output_df.iterrows():
        output_property_name = row["standard_property_name"]
        condition = standard_df["standard_property_name"] == output_property_name
        for column in standard_df.columns:
            if column.startswith("alternate_name"):
                condition |= standard_df[column] == output_property_name

        match = standard_df[condition]

        if not match.empty:
            output_df.at[index, "standard_property_name"] = match[
                "standard_property_name"
            ].values[0]
    return output_df


def update_ground_truth_extracted_standard_property_name(
    equipment_name, gt_property_names_df, ex_property_names_df
):
    """Update standard property names and by matching it with alternate names"""
    standard_df = get_standard_property_df(standard_property_name_list_path)
    chevron_asset_class_tag = equipment_name.split("_")[0].upper()
    asset_class = standard_df.loc[
        standard_df["chevron_asset_class_tag"].str.contains(
            chevron_asset_class_tag, na=False
        ),
        "asset_class",
    ].iloc[0]
    standard_property_name_df = get_specific_standard_df(standard_df, asset_class)
    extracted_property_names_df = update_standard_property_names(
        standard_property_name_df, ex_property_names_df
    )
    ground_truth_property_names_df = update_standard_property_names(
        standard_property_name_df, gt_property_names_df
    )
    return ground_truth_property_names_df, extracted_property_names_df


async def get_asset_names_from_s3(bucket, s3_file_path):
    """Get asset names from csv"""
    # df = pd.read_csv(file_path)
    df = await read_csv_from_storage(bucket, s3_file_path)
    df_cleaned = df.dropna()
    if "asset_name" not in df.columns:
        logger.error("asset_name not found in the csv file")
        return []
    equipment_name = (df_cleaned["asset_name"]).tolist()
    logger.info(f"equipment_name: {equipment_name}")
    return equipment_name


async def get_asset_details_from_s3(bucket, s3_file_path):
    """Get asset names and tag from csv"""
    df = await read_csv_from_storage(bucket, s3_file_path)
    df_cleaned = df.dropna()
    if "asset_name" not in df.columns or "asset_tag" not in df.columns:
        logger.error("asset_name or asset_tag not found in the csv file")
        return []
    equipment_name_tag = (
        df_cleaned["asset_name"] + " " + df_cleaned["asset_tag"]
    ).tolist()
    logger.info(f"equipment_name_tag: {equipment_name_tag}")
    return equipment_name_tag
