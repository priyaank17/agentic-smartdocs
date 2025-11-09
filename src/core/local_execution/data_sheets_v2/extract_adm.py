"""This script is used to extract the ADM data sheet from the raw JSON file in local."""

import os
import json
import asyncio
from src.utils.log import logger
from src.data_sheets_v2.get_adm_json.get_nodes_folder.adm import (
    get_adm_json,
)

# from src.data_sheets_v2.get_adm_json.get_nodes_folder.non_standard_adm import (
#     get_non_standard_adm_json,
# )
from src.data_sheets_v2.get_adm_json.property_mapping_loader import (
    prepare_asset_mapping,
)

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"


def load_config_and_necessary_variables():
    """Load config file and necessary variables for data sheet accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    config["RAW_JSON_FOLDER"] = config["datasheet_raw_json_folder_path"]
    config["ASSET_TYPE"] = config["asset_type"]
    config["ASSET_TABLE_PATH"] = config["asset_table_path"]
    config["ADM_JSON_FOLDER"] = config["datasheet_adms_folder_path"]
    return config


async def main():
    """Main function to extract ADM data from raw JSON files."""
    CONFIG = load_config_and_necessary_variables()
    RAW_JSON_FOLDER = CONFIG["RAW_JSON_FOLDER"]
    ASSET_TYPE = CONFIG["ASSET_TYPE"]
    ADM_JSON_FOLDER = CONFIG["ADM_JSON_FOLDER"]
    OTHER_JSON_FOLDER = CONFIG["datasheet_other_json_folder_path"]

    # # ASSET_TYPE = "heat_exchanger_shell_and_tube"
    # # ASSET_TYPE = "pump"
    # # ASSET_TYPE = "heat_exchanger_air_cooled"
    # # "heat_exchanger_air_cooler"
    # ASSET_TYPE = "drum"
    # RAW_JSON_FOLDER = rf"data\exxon\data_sheet\july_7\{ASSET_TYPE}"
    # ADM_JSON_FOLDER = rf"data\exxon\data_sheet\july_7\{ASSET_TYPE}\adm"
    # OTHER_JSON_FOLDER = rf"data\exxon\data_sheet\july_7\{ASSET_TYPE}\other"

    standard_property_field_mapping_df = await prepare_asset_mapping(ASSET_TYPE)
    # # save in json
    # with open("standard_property_field_mapping_df.json", "w", encoding="utf-8") as f:
    #     json.dump(standard_property_field_mapping_df, f, indent=2)
    # i = 1
    for file in os.listdir(RAW_JSON_FOLDER):
        if file.endswith(".raw.json"):
            RAW_PATH = os.path.join(RAW_JSON_FOLDER, file)

            OTHER_JSON_PATH_FOLDER = (
                OTHER_JSON_FOLDER + "/" + file.replace(".raw.json", "/")
            )
            document_id = file.replace(".raw.json", "")
            make_dirs = os.path.dirname(OTHER_JSON_PATH_FOLDER)
            os.makedirs(make_dirs, exist_ok=True)
            with open(RAW_PATH, "r", encoding="utf-8") as file_json:
                RAW_JSON = json.load(file_json)

            ADM_DATA = await get_adm_json(
                RAW_JSON,
                document_id,
                standard_property_field_mapping_df,
            )
            # NON_STANDARD_ADM_DATA = get_non_standard_adm_json(
            #     RAW_JSON,
            #     other_json_folder=OTHER_JSON_PATH_FOLDER,
            # )

            OUTPUT_PATH = os.path.join(ADM_JSON_FOLDER, file)
            output_json_path = OUTPUT_PATH.replace("raw", "adm")
            os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

            with open(rf"{output_json_path}", "w", encoding="utf-8") as f:
                json.dump(ADM_DATA, f, indent=2)
            # break


if __name__ == "__main__":
    asyncio.run(main())
