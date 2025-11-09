"""This module consists of utility functions for control narrative"""

import json
import os
from src.utils.log import logger

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"
CONFIG = None


def load_config(config_file_path):
    """Load config file"""
    with open(config_file_path, "r", encoding="utf-8") as config_file:
        return json.load(config_file)


def save_json(updated_received_assets_connections, json_file_name):
    """Save json"""
    logger.info("INIT: save json")
    config = load_config(CONFIG_FILE_PATH)
    json_file_path = os.path.join(
        ROOT_FOLDER_PATH, config["aggregrated_jsons_path"], json_file_name
    )
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(updated_received_assets_connections, json_file)
    logger.info(f"DONE: saved, {json_file_path}")
