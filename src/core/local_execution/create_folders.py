"""This module is responsible for creating folders."""
import json
import os
from src.utils.disc_utils import read_dict_from_json
from src.utils.log import logger

_CONFIG = read_dict_from_json("data/configs/config.json")


def create_folders():
    """Create folders."""
    logger.info("INIT: Local_Execution Create Folders")
    logger.info(f"_CONFIG = \n{json.dumps(_CONFIG, indent=4)}")

    for key, value in _CONFIG.items():
        # If the key ends with 'folder_path'
        if key.endswith("folder_path"):
            logger.info(f"Creating {value}")
            os.makedirs(value, exist_ok=True)
    logger.info("DONE: Local_Execution Create Folders")


if __name__ == "__main__":
    create_folders()
