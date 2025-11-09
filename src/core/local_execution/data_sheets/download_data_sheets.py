"""Local Script: Download Data Sheets."""

import os
import asyncio
# from src.app import lambda_handler
from py_unified_cloud_adapter.utils.errors import CloudAdapterException
from src.utils.log import logger

# from src.constants.Actions import Actions
from src.utils.disc_utils import read_dict_from_json
from src.utils.storage_utils import (
    fetch_file_via_adapter,
    upload_file_to_storage
)

_CONFIG = read_dict_from_json("data/configs/config.json")


async def download_data_sheets():
    """Downloads the data sheets."""
    try:
        logger.info("INIT: Downloading data sheets.")

        documents_list = await fetch_file_via_adapter(
            "",
            _CONFIG["documents_list_json_path"]
        )
        data_sheets_list = [
            doc for doc in documents_list if doc["type"] == "DATA SHEET"
        ]

        for i, data_sheet in enumerate(data_sheets_list):
            try:
                logger.info(
                    "Downloading data sheet %s/%s: %s",
                    i + 1,
                    len(data_sheets_list),
                    data_sheet["name"],
                )
                data_sheet_name = data_sheet["name"]
                if data_sheet["status"] != "GENERATED":
                    logger.info(
                        "ADM is not Available for %s. Skipping downloading ADM",
                        data_sheet_name,
                    )
                    continue

                data_sheet_key = (
                    f"public/{_CONFIG['plant_id']}/DOCS/DATA_SHEET/"
                    f"{data_sheet['id']}/{data_sheet['id']}.DATA_SHEET.adm.json"
                )
                logger.info(
                    "Downloading data sheet %s/%s: %s",
                    i + 1,
                    len(data_sheets_list),
                    data_sheet_name,
                )
                data_sheet_adm = await fetch_file_via_adapter(
                    os.environ["BUCKET"],
                    data_sheet_key
                )
                data_sheet_adm_local_path = (
                    f"{_CONFIG['data_sheet_adms_folder_path']}/"
                    f"{data_sheet_name}.data_sheet.adm.json"
                )
                await upload_file_to_storage(
                    "",
                    data_sheet_adm_local_path,
                    data_sheet_adm
                )

            except (FileNotFoundError, IOError) as e:
                logger.error("Could not download due to IO error: %s", e)
            except ValueError as e:
                logger.error("Could not download due to value error: %s", e)
            # pylint: disable=broad-except
            except Exception as e:
                logger.error("Unexpected error: %s", e)
        logger.info("DONE: Downloading data sheets.")
    except CloudAdapterException as e:
        logger.error("Error downloading data sheets: %s", e)


if __name__ == "__main__":
    asyncio.run(download_data_sheets())
