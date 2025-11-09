"""This module consists of functions to extract data sheet data in Local"""

import os
import json
import asyncio
from src.control_narrative_rag_junior.connection_data_extraction.extract_control_narrative import (
    get_control_instrument_adm,
    get_control_loop_adm,
)
from src.utils.log import logger

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
    # PLANT_ID = "dfe34e6b-2b5d-47d5-98dd-8a76d74f1334"
    # DOCUMENT_ID = "c52d1436-5937-487b-b189-6e22cdcbaa66"
    # BUCKET_NAME = "artisanbucketoregon133719-dev"
    CONTROL_LOOP_ADM_JSON_PATH = (
        "public/"
        + PLANT_ID
        + "/DOCS/CONTROL_NARRATIVE/"
        + DOCUMENT_ID
        + "/"
        + DOCUMENT_ID
        + ".CONTROL_NARRATIVE.junior.cl.adm.json"
    )
    INSTRUMENT_ADM_JSON_PATH = (
        "public/"
        + PLANT_ID
        + "/DOCS/CONTROL_NARRATIVE/"
        + DOCUMENT_ID
        + "/"
        + DOCUMENT_ID
        + ".CONTROL_NARRATIVE.junior.inst.adm.json"
    )
    MODEL_NAME = "gpt-4o"
    INPUT_FILES_PATH = {
        "bucket_name": BUCKET_NAME,
        "plant_id": PLANT_ID,
        "document_id": DOCUMENT_ID,
    }
    asyncio.run(get_control_loop_adm(INPUT_FILES_PATH, CONTROL_LOOP_ADM_JSON_PATH, MODEL_NAME))
    asyncio.run(get_control_instrument_adm(INPUT_FILES_PATH, INSTRUMENT_ADM_JSON_PATH, MODEL_NAME))
    # CONTROL_LOOP_ADM_JSON_PATH = (
    #     "data/local/mafpp/control_narrative/1_dec/1.updated_control_loop_data.json"
    # )
    # INSTRUMENT_ADM_JSON_PATH = (
    #     "data/local/mafpp/control_narrative/20_nov/1.control_narrative_instrument_data.json"
    # )
    # get_control_loop_adm(
    #     INPUT_FILES_PATH, CONTROL_LOOP_ADM_JSON_PATH, MODEL_NAME, save_to_local=True
    # )
    # get_control_instrument_adm(
    #     INPUT_FILES_PATH, INSTRUMENT_ADM_JSON_PATH, MODEL_NAME, save_to_local=True
    # )
