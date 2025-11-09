"""This module consists of functions for getting standard asset class"""

import numpy as np
import pandas as pd
from src.utils.log import logger
from src.data_sheets.constant import (
    get_standard_property_df,
    standard_property_name_list_path
)


def get_asset_class():
    """Returns the asset class"""
    logger.info("get standard asset_class")
    standard_property_name_df = get_standard_property_df(standard_property_name_list_path)
    standard_property_name_df = standard_property_name_df.replace({'asset_class': {np.nan: None}})
    standard_asset_class = standard_property_name_df['asset_class'].dropna().unique().tolist()
    logger.info(f"DONE: get standard asset_class, {standard_asset_class}")
    return standard_asset_class


def get_table_name():
    """Returns the table_name"""
    logger.info("get standard table_name")
    standard_property_name_df = get_standard_property_df(standard_property_name_list_path)
    possible_table_columns = standard_property_name_df.filter(like='possible_table_')
    unique_table_name = (pd.unique(possible_table_columns.values.ravel()).tolist())
    unique_table_name = [x for x in unique_table_name if pd.notna(x)]
    logger.info(f"DONE: get standard table_name, {unique_table_name}")
    return unique_table_name
