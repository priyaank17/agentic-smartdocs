"""This module consists of functions to extract data sheet data in Local"""

import os
import json
from src.control_narrative_lambda.control_narrative.extract_control_narrative_data import (
    extract_control_narrative_data,
)
from src.control_narrative_lambda.control_narrative.generate_adm import (
    generate_adm,
)
from src.utils.log import logger

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"


def load_config_and_necessary_variables():
    """Load config file and necessary variables for data sheet accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    control_narrative_path = os.path.join(
        ROOT_FOLDER_PATH, config["control_narrative_path"]
    )
    config["CONTROL_NARRATIVE_PATH"] = control_narrative_path
    config["PLANT_ID"] = config["plant_id"]
    config["DOCUMENT_ID"] = config["document_id"]
    config["BUCKET_NAME"] = config["bucket_name"]
    return config


if __name__ == "__main__":
    CONFIG = load_config_and_necessary_variables()
    PLANT_ID = CONFIG["PLANT_ID"]
    DOCUMENT_ID = CONFIG["DOCUMENT_ID"]
    BUCKET_NAME = CONFIG["BUCKET_NAME"]
    # PLANT_ID = "cd0a68f4-664f-4e83-937e-06ff06e8ce49"
    # DOCUMENT_ID = "0cb3facd-400b-4376-90d1-ae83653f5812"
    # BUCKET_NAME = "artisanbucketoregon18510-qatide"
    CONTROL_NARRATIVE_PATH = CONFIG["CONTROL_NARRATIVE_PATH"]
    INPUT_DATA_PATH = (
        f"public/{PLANT_ID}/DOCS/CONTROL_NARRATIVE/{DOCUMENT_ID}/input_data.json"
    )
    KEY_AGGREGATED_CONTROL_LOOPS = (
        f"{CONTROL_NARRATIVE_PATH}/aggregated_control_loops.json"
    )
    KEY_AGGREGATED_INSTRUMENTS = (
        f"{CONTROL_NARRATIVE_PATH}/"
        f"{DOCUMENT_ID}.CONTROL_NARRATIVE.inst.adm.json"
    )
    RECONCILED_CONTROL_LOOPS_PATH = (
        f"{CONTROL_NARRATIVE_PATH}/{DOCUMENT_ID}.CONTROL_NARRATIVE.cl.adm.json"
    )
    KEY_AGGREGATED_INFO = {
        "key_aggregated_control_loops": KEY_AGGREGATED_CONTROL_LOOPS,
        "key_aggregated_instruments": KEY_AGGREGATED_INSTRUMENTS,
    }
    extract_control_narrative_data(
        bucket_name=BUCKET_NAME,
        input_data_path=INPUT_DATA_PATH,
        reconciled_control_loops_path=RECONCILED_CONTROL_LOOPS_PATH,
        key_aggregated_info=KEY_AGGREGATED_INFO,
        local_path=True,
    )
    generate_adm(
        bucket_name=BUCKET_NAME,
        data_path=RECONCILED_CONTROL_LOOPS_PATH,
        config_data_key=INPUT_DATA_PATH,
        local_path=True,
    )
    generate_adm(
        bucket_name=BUCKET_NAME,
        data_path=KEY_AGGREGATED_INSTRUMENTS,
        config_data_key=INPUT_DATA_PATH,
        local_path=True,
    )
