"""Ingest data sheet."""

import json
import asyncio
import os
from src.utils.log import logger
from src.knowledge_graph_data_ingestion.ingest_data_sheet import (
    ingest_data_sheet,
)

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"


def load_config_and_necessary_variables():
    """Load config file and necessary variables for data sheet accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    config["ADMS_FOLDER_PATH"] = config["datasheet_adms_folder_path"]
    config["DATA_BASE_NAME"] = config["database_name"]
    config["PLANT_ID"] = config["plant_id"]
    return config


if __name__ == "__main__":
    CONFIG = load_config_and_necessary_variables()
    ADMS_FOLDER_PATH = CONFIG["ADMS_FOLDER_PATH"]
    DATA_BASE_NAME = CONFIG["DATA_BASE_NAME"]
    PLANT_ID = CONFIG["PLANT_ID"]

    # # ASSET_TYPE = "pump"
    # ASSET_TYPE = "heat_exchanger_air_cooled"
    # # ASSET_TYPE = "drum"
    # # ASSET_TYPE = "heat_exchanger_shell_and_tube"
    # # ADMS_FOLDER_PATH = (
    # #     # r"data\local\exxon\datasheet\sample_adms\with equipment subpart nozzles\29April"
    # #     fr"data\local\exxon\datasheet\sample_data\{ASSET_TYPE}\adm"
    # # )
    # ADMS_FOLDER_PATH = rf"data\exxon\data_sheet\sample_data\{ASSET_TYPE}\adm"
    # # ADMS_FOLDER_PATH = r"data\local\exxon\datasheet\sample_data"

    # DATA_BASE_NAME = "bceptestheatexchanger"
    # PLANT_ID = "data_sheet_test"

    for file in os.listdir(ADMS_FOLDER_PATH):
        if file.endswith(".adm.json"):
            ADM_PATH = os.path.join(ADMS_FOLDER_PATH, file)
            with open(ADM_PATH, "r", encoding="utf-8") as file_json:
                ADM = json.load(file_json)

            asyncio.run(ingest_data_sheet(ADM, DATA_BASE_NAME, PLANT_ID))

            logger.info(f"Data sheet {file} ingested successfully.")
            # break
