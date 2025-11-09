"""This module consists of functions to extract data sheet data in Local"""

import os
import json
from src.data_sheets.sheets_table_extraction.extract import get_data
from src.utils.log import logger

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"


def load_config_and_necessary_variables():
    """Load config file and necessary variables for data sheet accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    config["PLANT_ID"] = config["plant_id"]
    config["DOCUMENT_ID"] = config["document_id"]
    return config


if __name__ == "__main__":
    CONFIG = load_config_and_necessary_variables()
    PLANT_ID = CONFIG["PLANT_ID"]
    DOCUMENT_ID = CONFIG["DOCUMENT_ID"]
    # DOCUMENT_ID = "d3193743-18f6-4eeb-b611-cbbb0da400aa"
    # PLANT_ID = "499df0e0-5ede-4330-875a-c3e2f7881848"
    DATA_SHEET_PATH = f"public/{PLANT_ID}/DOCS/DATA_SHEET/{DOCUMENT_ID}"
    INPUT_DATA_PATH = f"{DATA_SHEET_PATH}/input_data.json"
    # get_data(INPUT_DATA_PATH, local_path=True)    # to extract data sheet table
    get_data(INPUT_DATA_PATH, os.getenv("BUCKET"))    # to extract data sheet table
