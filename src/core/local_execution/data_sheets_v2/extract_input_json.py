"""Extracts bounding boxes from document intelligence JSON data."""

import asyncio
import json
import os
from src.data_sheets_v2.prepare_input.get_input_data import (
    # prepare_table_extraction_data,
    prepare_table_extraction_data_vision,
    # parse_pages,
)
from src.utils.log import logger

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"


def load_config_and_necessary_variables():
    """Load config file and necessary variables for data sheet accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")

    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        logger.error(f"Config file not found at {CONFIG_FILE_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise

    # Validate required keys
    required_keys = ["document_id", "plant_id"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required config keys: {missing_keys}")

    config["DOCUMENT_ID"] = config["document_id"]
    config["PLANT_ID"] = config["plant_id"]
    config["BUCKET"] = os.getenv("BUCKET", "default-bucket-name")
    return config


async def main():
    """Main function to prepare input data for table extraction."""
    CONFIG = load_config_and_necessary_variables()
    PLANT_ID = CONFIG["PLANT_ID"]
    DOCUMENT_ID = CONFIG["DOCUMENT_ID"]
    BUCKET = CONFIG["BUCKET"]

    # PLANT_ID = "a8bea74c-cbe9-4aad-8cc6-6f2c8b96291d"
    # DOCUMENT_ID = "f6ec0770-9b56-401f-a259-f274d0bf732e"
    # BUCKET = "plants"
    # # # PATH = r"C:\Users\krishnajajoo\Desktop\drishya\smart-document-components\data\image_data"
    PATH = f"{PLANT_ID}/documents/data_sheet/{DOCUMENT_ID}"
    # # INPUT_DATA = await prepare_table_extraction_data(
    # #     BUCKET, PATH, DOCUMENT_ID, PLANT_ID
    # # )

    INPUT_DATA = await prepare_table_extraction_data_vision(
        BUCKET, PATH, DOCUMENT_ID, PLANT_ID
    )

    print("==============================================")
    # print("Final Input Data:", INPUT_DATA)
    with open(
        "input_data.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(INPUT_DATA, f, indent=4)

    # """Main function to run the parser with hardcoded paths for testing."""

    # # workdir = "src/local_execution/output"
    # # Path(workdir).mkdir(parents=True, exist_ok=True)
    # BUCKET = "plants"

    # image_path_list = [
    #     "a8bea74c-cbe9-4aad-8cc6-6f2c8b96291d/documents/
    # data_sheet/f6ec0770-9b56-401f-a259-f274d0bf732e/
    # 18932c98-5bac-40ec-b25b-ab99c30d46f6+2200X1700+3",
    # ]

    # input_data = await parse_pages(BUCKET, image_path_list)

    # input_json_path = "src/local_execution/output/input.json"

    # with open(input_json_path, "w", encoding="utf-8") as f:
    #     json.dump(input_data, f, indent=2, ensure_ascii=False)

    # print(f"Extraction saved to: {input_json_path}")


if __name__ == "__main__":
    asyncio.run(main())
