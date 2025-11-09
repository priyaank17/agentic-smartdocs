"""This module downloads HMB documents"""
import os
import asyncio
from src.utils.storage_utils import (
    fetch_file_via_adapter, upload_file_to_storage)
from src.utils.log import logger
from src.utils.disc_utils import read_dict_from_json

_CONFIG = read_dict_from_json("data/configs/config.json")


async def download_hmb_adms():
    """This function downloads HMB ADMs"""
    logger.info("INIT: Downloading HMB ADMs.")

    documents_list = await fetch_file_via_adapter(
        "",
        _CONFIG["documents_list_json_path"]
    )
    hmb_docs_list = [doc for doc in documents_list if doc["type"] == "HMB"]

    for i, hmb_doc in enumerate(hmb_docs_list):
        logger.info(
            f"Downloading HMB ADM {i + 1}/{len(hmb_docs_list)}: {hmb_doc['name']}"
        )
        hmb_doc_name = hmb_doc["name"]
        if hmb_doc["status"] != "GENERATED":
            logger.info(
                f"ADM is not Available for {hmb_doc_name}. Skipping downloading ADM"
            )
            continue

        hmb_s3_key = f"""public/{_CONFIG['plant_id']
                                 }/DOCS/HMB/{hmb_doc['id']}/{hmb_doc['id']}.HMB.adm.json"""
        logger.info(
            f"Downloading HMB ADM {i + 1}/{len(hmb_docs_list)}: {hmb_s3_key}"
        )
        logger.info(
            f"Downloading HMB ADM {i + 1}/{len(hmb_docs_list)}: {hmb_doc_name}"
        )
        try:
            hmb_adm = await fetch_file_via_adapter(
                os.environ["BUCKET"],
                hmb_s3_key
            )
            hmb_adm_local_path = f"""{
                _CONFIG['hmb_adms_folder_path']}/{hmb_doc_name}.hmb.adm.json"""
            await upload_file_to_storage("", hmb_adm_local_path, hmb_adm)
        except BaseException as e:
            logger.error(f"Error downloading HMB ADM: {e}")
    logger.info("DONE: Downloading HMB ADMs.")


if __name__ == "__main__":
    asyncio.run(download_hmb_adms())
