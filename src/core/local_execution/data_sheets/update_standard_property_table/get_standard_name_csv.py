"""This module contains functions to get standard name csv.
First download the Asset_Class_Standard_Properties.xlsx from drive and save in data folder
add this files info in config.json as
"raw_standard_property_sheet_path": "data/Asset_Class_Standard_Properties.xlsx"
"""

import pandas as pd
from src.utils.log import logger
from src.data_sheets.constant import (
    standard_property_name_list_path,
)
from src.utils.disc_utils import read_dict_from_json

_CONFIG = read_dict_from_json("data/configs/config.json")


def get_df_file(file_path):
    """Returns a DataFrame from a CSV file"""
    xls = pd.ExcelFile(file_path)
    dfs = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
    combined_df = pd.concat(dfs.values(), ignore_index=True)
    output_csv_file = standard_property_name_list_path
    combined_df.to_csv(output_csv_file, index=False)
    logger.info(f"Combined data saved to {output_csv_file}")
    return combined_df


if __name__ == "__main__":
    RAW_STANDARD_PROPERTY_SHEET_PATH = _CONFIG["raw_standard_property_sheet_path"]
    filtered_df = get_df_file(RAW_STANDARD_PROPERTY_SHEET_PATH)
