"""This module consists of functions to extract data sheet data in Local"""

import os
import json
from src.data_sheets_v2.extract_table_data.extract import extract_table_data
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
    # CONFIG = load_config_and_necessary_variables()
    PLANT_ID = "cd0a68f4-664f-4e83-937e-06ff06e8ce49"
    DOCUMENT_ID = "f6ec0770-9b56-401f-a259-f274d0bf732e"
    # # PLANT_ID = "499df0e0-5ede-4330-875a-c3e2f7881848"
    # # DOCUMENT_ID = "143ff74a-06ad-441a-bec8-c3abf69be2b0"
    # PLANT_ID = "ef2aa057-2f9c-453b-9990-dcb4459a4355"
    # # DOCUMENT_ID = "f4839696-4345-4cce-bedc-b413ea5259b9"
    # DOCUMENT_ID = "a4dd2a67-9b3f-49c9-b306-f94f08542210"
    # # "6728bf7d-22ba-4663-84f0-e514b5fc5c37"
    # # "76b5e676-5442-453a-8fb6-35036b34f542"
    # PATH = f"public/{PLANT_ID}/DOCS/DATA_SHEET/{DOCUMENT_ID}"
    S3_BUCKET = os.getenv("BUCKET", "default-bucket-name")
    INPUT_DATA_PATH = "data/input_data.json"
    MODEL_NAME = "gpt-4o"
    import asyncio

    async def main():
        """."""
        await extract_table_data(INPUT_DATA_PATH, S3_BUCKET, MODEL_NAME, save_local=True)

    asyncio.run(main())
