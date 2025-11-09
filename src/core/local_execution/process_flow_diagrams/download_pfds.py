"""This module downloads the Process Flow Diagrams (PFD) ADMs from S3 to the local environment."""

import os
import asyncio
from src.utils.storage_utils import (fetch_file_via_adapter
                                     , upload_file_to_storage)
from src.utils.log import logger
from src.utils.disc_utils import read_dict_from_json

_CONFIG = read_dict_from_json("data/configs/config.json")


async def download_pfd_adms():
    """This function downloads PFD ADMs"""
    logger.info("INIT: Downloading pfd ADMs.")

    documents_list = await fetch_file_via_adapter(
        "",
        _CONFIG["documents_list_json_path"]
    )
    pfd_docs_list = [
        doc for doc in documents_list if doc["type"] == "PROCESS FLOW DIAGRAM"
    ]

    for i, pfd_doc in enumerate(pfd_docs_list):
        logger.info(
            f"Downloading pfd ADM {i + 1}/{len(pfd_docs_list)}: {pfd_doc['name']}"
        )
        pfd_doc_name = pfd_doc["name"]
        if pfd_doc["status"] != "GENERATED":
            logger.info(
                f"ADM is not Available for {pfd_doc_name}. Skipping downloading ADM"
            )
            continue

        pfd_key = (
            f"public/{_CONFIG['plant_id']}/DOCS/process_flow_diagram/"
            f"{pfd_doc['id']}.process_flow_diagrams.adm.json"
        )

        logger.info(f"Downloading pfd ADM {i + 1}/{len(pfd_docs_list)}: {pfd_doc_name}")
        pfd_adm = await fetch_file_via_adapter(
            os.environ["BUCKET"],
            pfd_key
        )
        pfd_adm_local_path = (
            f"{_CONFIG['process_flow_diagrams_folder_path']}/"
            f"{pfd_doc_name}.process_flow_diagrams.adm.json"
        )

        await upload_file_to_storage("", pfd_adm_local_path, pfd_adm)
    logger.info("DONE: Downloading pfd ADMs.")


if __name__ == "__main__":
    asyncio.run(download_pfd_adms())
