"""This module consists of functions to extract data sheet data in Local"""

import os
import json
from src.data_sheets.sheet_adm_generation.generate_adm import generate_adm
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
    # DOCUMENT_ID = "5e62ae4a-ba95-430f-af00-d1ed48b4ff53"
    # PLANT_ID = "499df0e0-5ede-4330-875a-c3e2f7881848"
    DATA_SHEET_PATH = f"public/{PLANT_ID}/DOCS/DATA_SHEET/{DOCUMENT_ID}"
    INPUT_DATA_PATH = f"public/{PLANT_ID}/DOCS/DATA_SHEET/{DOCUMENT_ID}/input_data.json"
    generate_adm(INPUT_DATA_PATH, DATA_SHEET_PATH, os.getenv("BUCKET", "default-bucket-name"))
    # DATA_SHEET_PATH = "data/sanha_dev/data_sheets/prompt_responses"
    # generate_adm(
    #     INPUT_DATA_PATH,
    #     DATA_SHEET_PATH,
    #     output_folder_local_path="tests/test_data/sanha/data_sheets/adms",
    #     is_csv_local_path=True
    # )
