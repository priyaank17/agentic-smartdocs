"""This module contains functions for extracting table data from CSV files."""

import warnings
import os
import pandas as pd
import numpy as np
from src.utils.log import logger
from src.data_sheets.constant import (
    columns_cba_operating_conditions,
    columns_operating_conditions,
    columns_maximum_loading_case,
    columns_minimum_loading_case,
    columns_table_format_1_data,
    drop_columns_table_format_2_data,
    drop_columns_nozzle,
)

warnings.filterwarnings("ignore")


def get_subpart_name(key):
    """Return subpart name based on key."""
    subparts = {
        "section_a": "SECTION_A",
        "section_b": "SECTION_B",
        "section_c": "SECTION_C",
        "shell_side": "SHELL_SIDE",
        "tube_side": "TUBE_SIDE",
    }
    for part, name in subparts.items():
        if part in key:
            return name
    return None


def drop_columns_if_exist(df, columns):
    """Drop specified columns from DataFrame if they exist."""
    df.drop(columns=[col for col in columns if col in df.columns], inplace=True)


def append_property(
    json_data,
    row,
    value,
    section,
    **kwargs,
):
    """Append a property to the json_data."""
    context_name = kwargs.get(
        "context_name", "EQUIPMENT"
    )  # Retrieve other optional arguments
    connection_type = kwargs.get("connection_type")
    subpart_name = kwargs.get("subpart_name")
    nozzle_number = kwargs.get("nozzle_number")
    page_number = kwargs.get("page_number")
    context = {
        "context_name": context_name,
        "equipment_name": None,
        "connection_type": connection_type,
        "subpart_name": subpart_name,
    }

    if context_name == "NOZZLE":
        context["nozzle_number"] = nozzle_number

    json_data["properties"].append(
        {
            "property_name": row["property_name"],
            "standard_property_name": row["standard_property_name"],
            "property_value": value,
            "property_notes": None,
            "data_sheet_section": section,
            "property_details": None,
            "context": context,
            "page_number": page_number,
        }
    )


def process_table(json_data, csv_file_path, section, **kwargs):
    """Process a table from a CSV file and append data to json_data."""
    logger.info(f"INIT: {section} function initialized")
    context_name = kwargs.get("context_name", "EQUIPMENT")
    drop_columns = kwargs.get("drop_columns", None)
    column_subset = kwargs.get("column_subset", None)
    nozzle_number = kwargs.get("nozzle_number", None)
    page_number = kwargs.get("page_number", None)
    df = pd.read_csv(csv_file_path)
    if drop_columns:
        drop_columns_if_exist(df, drop_columns)
    if column_subset:
        df = df[column_subset]
    df.replace({np.nan: None}, inplace=True)
    for _, row in df.iterrows():
        for key, value in row.items():
            key = key.lower()
            if key not in ["property_name", "standard_property_name"]:
                subpart_name = get_subpart_name(key)
                connection_type = (
                    "INLET" if "inlet" in key else "OUTLET" if "outlet" in key else None
                )
                append_property(
                    json_data,
                    row,
                    value,
                    section,
                    context_name=context_name,
                    connection_type=connection_type,
                    subpart_name=subpart_name,
                    nozzle_number=nozzle_number,
                    page_number=page_number,
                )
    logger.info(f"Done: {section} function executed")
    return json_data


def nozzles_table(json_data, csv_file_path, page_number):
    """Process nozzles table."""
    logger.info("INIT: nozzles_table function initialized")
    df = pd.read_csv(csv_file_path)
    df.replace({np.nan: None}, inplace=True)
    drop_columns_if_exist(df, drop_columns_nozzle)
    n = 1
    for _, row in df.iterrows():
        row_iter = iter(row.items())
        property_details = dict(row_iter)
        nozzle_number = property_details.pop("nozzle_number", None)
        subpart_name = property_details.pop("subpart_name", None)
        connection_type = property_details.pop("connection_type", None)
        if connection_type is not None:
            connection_type = connection_type.upper()
        if subpart_name:
            if "shell" in subpart_name.lower() and "side" in subpart_name.lower():
                subpart_name = "SHELL_SIDE"
            elif "tube" in subpart_name.lower() and "side" in subpart_name.lower():
                subpart_name = "TUBE_SIDE"
            elif "feed" in subpart_name.lower() and "gas" in subpart_name.lower():
                subpart_name = "SECTION_A"
            elif "residue" in subpart_name.lower() and "gas" in subpart_name.lower():
                subpart_name = "SECTION_B"
            elif "hp" in subpart_name.lower() and "sep" in subpart_name.lower():
                subpart_name = "SECTION_C"
        else:
            subpart_name = f"UNNAMED_SUBPART_{n}"
            n += 1
        nozzle_number = row["nozzle_number"]
        json_data["properties"].append(
            {
                "property_name": "nozzle_number",
                "standard_property_name": "nozzle_number",
                "property_value": nozzle_number,
                "property_notes": None,
                "data_sheet_section": "NOZZLES",
                "property_details": property_details,
                "context": {
                    "context_name": "NOZZLE",
                    "equipment_name": None,
                    "connection_type": connection_type,
                    "subpart_name": subpart_name,
                    "nozzle_number": nozzle_number,
                },
                "page_number": page_number,
            }
        )
    logger.info("Done: nozzles_table function executed")
    return json_data


def get_correct_details(data):
    """Update context based on standard_property_name."""
    for item in data:
        if item["data_sheet_section"] == "OPERATING_CONDITIONS":
            standard_property_name = item["standard_property_name"].lower()
            context = item["context"]
            if "inlet" in standard_property_name or "suction" in standard_property_name:
                context.update(
                    {
                        "context_name": "NOZZLE",
                        "connection_type": "INLET",
                        "nozzle_number": None,
                    }
                )
            elif (
                "outlet" in standard_property_name
                or "discharge" in standard_property_name
            ):
                context.update(
                    {
                        "context_name": "NOZZLE",
                        "connection_type": "OUTLET",
                        "nozzle_number": None,
                    }
                )
    return data


def operating_conditions_cba(json_data, csv_file_path):
    """Process operating conditions for cba."""
    logger.info("INIT: operating_conditions_cba function initialized")
    df = pd.read_csv(csv_file_path)
    selected_df = df[columns_cba_operating_conditions]
    selected_df.replace({np.nan: None}, inplace=True)
    for _, row in selected_df.iterrows():
        property_name = row["property_name"]
        for key, value in row.items():
            if key not in ("property_name", "standard_property_name"):
                json_data["properties"].append(
                    {
                        "property_name": property_name,
                        "standard_property_name": row["standard_property_name"],
                        "property_value": value,
                        "property_notes": None,
                        "data_sheet_section": "OPERATING_CONDITIONS",
                        "property_details": None,
                        "context": {
                            "context_name": "EQUIPMENT",
                            "equipment_name": key.split("_")[-1].upper(),
                            "connection_type": None,
                            "subpart_name": key.split("_")[-1].upper(),
                        },
                    }
                )
    get_correct_details(json_data["properties"])
    logger.info("Done: operating_conditions_cba function executed")
    return json_data


def operating_conditions(json_data, csv_file_path):
    """Process operating conditions."""
    return process_table(
        json_data,
        csv_file_path,
        "OPERATING_CONDITIONS",
        column_subset=columns_operating_conditions,
    )


def maximum_loading_case(json_data, csv_file_path):
    """Process maximum loading case data."""
    return process_table(
        json_data,
        csv_file_path,
        "MAXIMUM_LOADING_CASE",
        column_subset=columns_maximum_loading_case,
    )


def minimum_loading_case(json_data, csv_file_path):
    """Process minimum loading case data."""
    file_name = csv_file_path.split(".")[0]
    nozzle_number = file_name.split("_")[-1].upper()
    return process_table(
        json_data,
        csv_file_path,
        "MINIMUM_LOADING_CASE",
        context_name="NOZZLE",
        column_subset=columns_minimum_loading_case,
        nozzle_number=nozzle_number,
    )


def remove_appearance_number(table_name, appearance_number):
    """Remove appearance number from table name."""
    if appearance_number is not None and appearance_number > 1:
        return "_".join(table_name.split("_")[:-1])
    return table_name


def table_format_1(
    json_data, csv_file_path, appearance_number, page_number
):  # for unstructured format (having property name only)
    """Process data."""
    logger.info(f"INIT: {csv_file_path} function initialized")
    file_name = os.path.basename(csv_file_path)
    table_name = file_name.split(".")[0].upper()
    table_name = remove_appearance_number(table_name, appearance_number)
    last_word = table_name.split("_")[-1]
    if len(last_word) < 3:
        nozzle_number = last_word
        return process_table(
            json_data,
            csv_file_path,
            "MINIMUM_LOADING_CASE",
            context_name="NOZZLE",
            column_subset=columns_minimum_loading_case,
            nozzle_number=nozzle_number,
            page_number=page_number,
        )
    if table_name == "DESCRIPTION":
        return process_table(
            json_data,
            csv_file_path,
            "DESCRIPTION",
            context_name="META_DATA",
            column_subset=columns_table_format_1_data,
            page_number=page_number,
        )
    return process_table(
        json_data,
        csv_file_path,
        table_name,
        column_subset=columns_table_format_1_data,
        page_number=page_number,
    )


def table_format_2(
    json_data, csv_file_path, asset_class, appearance_number, page_number
):  # having columns and properties (performance of unit, construction)
    """Process data having columns and properties"""
    logger.info(f"INIT: {csv_file_path} function initialized")
    file_name = os.path.basename(csv_file_path)
    table_name = file_name.split(".")[0].upper()
    table_name = remove_appearance_number(table_name, appearance_number)
    last_word = table_name.split("_")[-1]
    if table_name == "OPERATING_CONDITIONS" and asset_class == "CBA":
        return operating_conditions_cba(json_data, csv_file_path)
    if len(last_word) < 3:
        nozzle_number = last_word
        return process_table(
            json_data,
            csv_file_path,
            "MINIMUM_LOADING_CASE",
            context_name="NOZZLE",
            column_subset=columns_minimum_loading_case,
            nozzle_number=nozzle_number,
            page_number=page_number
        )
    return process_table(
        json_data,
        csv_file_path,
        table_name,
        drop_columns=drop_columns_table_format_2_data,
        context_name="NOZZLE",
        page_number=page_number
    )


def table_format_3(
    json_data, csv_file_path, appearance_number, page_number
):  # having column names only
    """Process data of table_format 3"""
    logger.info(f"INIT: {csv_file_path} function initialized")
    file_name = os.path.basename(csv_file_path)
    table_name = file_name.split(".")[0].upper()
    table_name = remove_appearance_number(table_name, appearance_number)
    df = pd.read_csv(csv_file_path)
    df.replace({np.nan: None}, inplace=True)
    df.drop(columns=["Unnamed: 0"], inplace=True)
    for _, row in df.iterrows():
        row_iter = iter(row.items())
        first_key, first_value = next(row_iter)
        property_details = dict(row_iter)
        json_data["properties"].append(
            {
                "property_name": first_key,
                "standard_property_name": first_key,
                "property_value": first_value,
                "property_notes": None,
                "data_sheet_section": table_name,
                "property_details": property_details,
                "context": {
                    "context_name": table_name,
                    "equipment_name": None,
                    "connection_type": None,
                    "subpart_name": None,
                    "nozzle_number": None,
                },
                "page_number": page_number,
            }
        )
