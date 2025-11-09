"""
This module contains functions for postprocessing data sheets."""
from src.utils.log import logger


def convert_unicode_to_boolean(data):
    """
    Converts Unicode characters in the input data to boolean values.
    \u25cf -> True
    \u25cb -> False
    """
    property_data = data.get('data', [])

    for row in property_data:
        for key, value in row.items():
            if value in ("\u25cf", "●"):  # Black Circle (●)
                row[key] = "True"
            elif value in ("\u25cb", "○"):  # White Circle (○)
                row[key] = ""
    return data


def rename_empty_columns(json_data):
    """
    Renames empty column names in the input JSON data.
    """
    logger.info("INIT: Renaming empty column names")
    column_names = json_data["column_names"]
    data = json_data["data"]

    # Rename empty column names
    unnamed_counter = 1
    updated_column_names = []
    column_name_mapping = {}

    for col in column_names:
        if col == "":
            new_col_name = f"Unnamed Column {unnamed_counter}"
            updated_column_names.append(new_col_name)
            column_name_mapping[""] = new_col_name  # Map empty names
            unnamed_counter += 1
        else:
            updated_column_names.append(col)
            column_name_mapping[col] = col  # Map existing names

    # Update data with renamed columns
    updated_data = []
    for row in data:
        updated_row = {}
        for key, value in row.items():
            new_key = column_name_mapping.get(key, key)
            updated_row[new_key] = value
        updated_data.append(updated_row)

    # Update the JSON
    json_data["column_names"] = updated_column_names
    json_data["data"] = updated_data
    logger.info("DONE: Renamed empty column names")
    return json_data
