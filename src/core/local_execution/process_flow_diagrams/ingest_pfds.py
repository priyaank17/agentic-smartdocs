"""This module ingests the Process Flow Diagrams (PFD) ADMs"""

import os
from src.app import lambda_handler
from src.utils.log import logger
from src.constants.Actions import Actions
from src.utils.disc_utils import read_dict_from_json

# Read configuration data
_CONFIG = read_dict_from_json("data/configs/config.json")


def get_event_payload(pfd_path):
    """This function returns event payload"""
    action = Actions.INGEST_PFD_INTO_NEO4J
    return {
        "body": {
            "action": action,
            "plant_id": _CONFIG["plant_id"],
            "adm_path": pfd_path,
        }
    }


async def ingest_pfd_files():
    """This function ingests PFD files"""
    logger.info("INIT: Ingesting PFD files - LOCAL ENVIRONMENT")

    pfd_files_folder_path = _CONFIG["process_flow_diagrams_folder_path"]
    file_list = os.listdir(pfd_files_folder_path)
    for i, file_name in enumerate(file_list, start=1):
        logger.info(f"Ingesting file {i}: {file_name} {i}/{len(file_list)}")
        pfd_path = os.path.join(pfd_files_folder_path, file_name)
        event_payload = get_event_payload(pfd_path)
        await lambda_handler(event_payload, request="")

    logger.info("DONE: Ingesting PFD files - LOCAL ENVIRONMENT")


if __name__ == "__main__":
    ingest_pfd_files()
