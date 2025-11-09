"""This module consists of functions to extract data sheet data in Local"""

import os
import json
from src.process_narrative_rag_junior.extract_equipment_operating_conditions import (
    extract_narrative
)
from src.utils.log import logger

get_equipment_operating_data = extract_narrative.get_equipment_operating_data
ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"


def load_config_and_necessary_variables():
    """Load config file and necessary variables for data sheet accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    process_narrative_path = os.path.join(
        ROOT_FOLDER_PATH, config["control_narrative_path"]
    )
    config["PROCESS_NARRATIVE_PATH"] = process_narrative_path
    config["PLANT_ID"] = config["plant_id"]
    config["DOCUMENT_ID"] = config["document_id"]
    config["BUCKET_NAME"] = config["bucket_name"]
    return config


if __name__ == "__main__":
    CONFIG = load_config_and_necessary_variables()
    PLANT_ID = CONFIG["PLANT_ID"]
    DOCUMENT_ID = CONFIG["DOCUMENT_ID"]
    BUCKET_NAME = CONFIG["BUCKET_NAME"]
    PROCESS_NARRATIVE_PATH = CONFIG["PROCESS_NARRATIVE_PATH"]
    # ADM_JSON_PATH = (
    #     "public/"
    #     + PLANT_ID
    #     + "/DOCS/PROCESS_NARRATIVE/"
    #     + DOCUMENT_ID
    #     + "/"
    #     + DOCUMENT_ID
    #     + ".PROCESS_NARRATIVE.junior.oc.adm.json"
    # )
    MODEL_NAME = "gpt-4o"
    # PLANT_ID = "499df0e0-5ede-4330-875a-c3e2f7881848"
    # DOCUMENT_ID = "8778c671-94e9-4f3f-a424-7ad80d85c6af"
    # BUCKET_NAME = "artisanbucketoregon133719-dev"
    # PROCESS_NARRATIVE_PATH = "data/local/mafpp/process_narrative/17_dec"
    ADM_JSON_LOCAL_PATH = PROCESS_NARRATIVE_PATH + "/4.PROCESS_NARRATIVE.oc.adm.json"
    os.makedirs(os.path.dirname(ADM_JSON_LOCAL_PATH), exist_ok=True)
    INPUT_FILES_PATH = {
        "bucket_name": BUCKET_NAME,
        "document_id": DOCUMENT_ID,
        "plant_id": PLANT_ID,
    }
    # get_equipment_operating_data(
    #     INPUT_FILES_PATH,
    #     MODEL_NAME,
    #     ADM_JSON_PATH,
    # )
    get_equipment_operating_data(
        INPUT_FILES_PATH,
        MODEL_NAME,
        ADM_JSON_LOCAL_PATH,
        save_to_local=True,
    )
