"""This script downloads all the process narratives from
the S3 bucket and stores them in the local folder."""

import os
import asyncio
from src.utils.storage_utils import (fetch_file_via_adapter
                                     , upload_file_to_storage)
from src.utils.log import logger
from src.utils.disc_utils import read_dict_from_json

_CONFIG = read_dict_from_json("data/configs/config.json")


async def download_process_narratives():
    """Download Process Narratives."""
    logger.info("INIT: Downloading Process Narratives.")

    documents_list = await fetch_file_via_adapter(
        "",
        _CONFIG["documents_list_json_path"]
    )
    process_narratives_list = [
        doc for doc in documents_list if doc["type"] == "PROCESS NARRATIVE"
    ]

    for i, process_narrative in enumerate(process_narratives_list):
        narrative_num = f"{i + 1}/{len(process_narratives_list)}"
        narrative_name = process_narrative['name']
        logger.info(f"Downloading Narrative {narrative_num}")
        logger.info(f"Narrative Name: {narrative_name}")
        if process_narrative["status"] != "GENERATED":
            logger.info(
                f"""Process Narrative is not available for {narrative_name}.
                Skipping downloading Process Narrative."""
            )
            continue
        path = f"{_CONFIG['plant_id']}/documents/{process_narrative['id']}"
        narrative_s3_key = path + ".process_narrative.adm.json"
        narrative_s3_key = (
            f"""public/{_CONFIG['plant_id']}/documents/process_narrative/{process_narrative['id']}/{
                process_narrative['id']}.PROCESS_NARRATIVE.adm.json"""
        )
        length = len(process_narratives_list)
        logger.info(
            f"Downloading Process Narrative {i + 1}/{length}: {narrative_name}"
        )
        narrative_data = await fetch_file_via_adapter(
            os.environ["BUCKET"],
            narrative_s3_key
        )
        narrative_local_path = (
            f"{_CONFIG['process_narratives_folder_path']}/{process_narrative['id']}"
            + ".pnd.adm.json"
        )
        await upload_file_to_storage("", narrative_local_path, narrative_data)
    logger.info("DONE: Downloading Process Narratives.")


if __name__ == "__main__":
    asyncio.run(download_process_narratives())
