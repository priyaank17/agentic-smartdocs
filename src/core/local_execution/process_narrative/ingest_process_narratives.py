"""This module contains functions to ingest HMB ADMs"""

import os

from src.app import lambda_handler
from src.utils.log import logger
from src.constants.Actions import Actions
from src.utils.disc_utils import read_dict_from_json


_CONFIG = read_dict_from_json("data/configs/config.json")


def get_event_payload(pnds_path):
    """This function returns event payload"""
    action = Actions.INGEST_PROCESS_NARRATIVE_ADM_INTO_NEO4J
    return {
        "body": {
            "action": action,
            "plant_id": _CONFIG["plant_id"],
            "adm_path": pnds_path,
        }
    }


def ingest_pnds():
    """This function ingests HMB files"""
    logger.info("INIT: Ingesting PNDS files - LOCAL ENVIRONMENT")

    process_narratives_folder_path = _CONFIG["process_narratives_folder_path"]
    file_list = os.listdir(process_narratives_folder_path)
    for i, file_name in enumerate(file_list, start=1):
        logger.info(f"Ingesting file {i}: {file_name} {i}/{len(file_list)}")
        pnds_path = os.path.join(process_narratives_folder_path, file_name)
        event_payload = get_event_payload(pnds_path)
        lambda_handler(event_payload, request="")

    logger.info("DONE: Ingesting PNDS files - LOCAL ENVIRONMENT")


if __name__ == "__main__":
    ingest_pnds()
