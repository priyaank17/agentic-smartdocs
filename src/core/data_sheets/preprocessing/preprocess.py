"""This file would be used to preprocess ocr data"""

from src.utils.log import logger
from src.data_sheets.preprocessing.pre_process_ocr_data import (
    sorted_ocr_for_property_name_string,
    sorted_ocr_data_for_data_sheet_table,
)


def add_table_name(word_positions_from_ocr, table_name):
    """Add table name to ocr highlight bounding box"""
    for item in word_positions_from_ocr:
        item["data_sheet_section"] = table_name.upper()
    return word_positions_from_ocr


def get_table_ocr_coordinates_data(ocr_data_sheet_json_data, table_config):
    """Get ocr bounding box data"""
    table_name = table_config.get("table_name")
    bounding_box = table_config.get("bounding_coordinates")
    word_positions_from_ocr, _ = sorted_ocr_data_for_data_sheet_table(
        ocr_data_sheet_json_data, bounding_box
    )
    word_positions_from_ocr = add_table_name(word_positions_from_ocr, table_name)
    return word_positions_from_ocr


def pre_process_data_sheet(ocr_data_sheet_json_data, bounding_box):
    """Pre-process data sheet"""
    logger.info("INIT: Preprocess ocr json data sheet output")
    _, sorted_ocr_data = sorted_ocr_data_for_data_sheet_table(
        ocr_data_sheet_json_data, bounding_box
    )
    # logger.info(sorted_ocr_data)
    logger.info("DONE: Pre processed ocr json data sheet data to get table data.")
    return sorted_ocr_data


def pre_process_ocr_property_name(ocr_data_sheet_json_data, bounding_box):
    """
    Pre-processes the OCR data sheet to extract the property name.

    Args:
        ocr_data_sheet_json_data (dict): The OCR data sheet in JSON format.
        bounding_box (tuple): The bounding box coordinates.

    Returns:
        list: The sorted OCR data.
    """
    logger.info("INIT: Preprocess ocr json data to get property name")
    sorted_ocr_data = sorted_ocr_for_property_name_string(
        ocr_data_sheet_json_data, bounding_box
    )
    # logger.info(sorted_ocr_data)
    logger.info("DONE: Pre processed ocr json data to get property name of that table.")
    return sorted_ocr_data
