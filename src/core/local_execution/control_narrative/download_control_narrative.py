"""This script downloads all the process narratives from
the S3 bucket and stores them in the local folder."""

import os
import asyncio
from src.utils.storage_utils import (
    fetch_file_via_adapter, upload_file_to_storage)
from src.utils.log import logger
from src.utils.disc_utils import read_dict_from_json


_CONFIG = read_dict_from_json("data/configs/config.json")


async def download_control_narrative():
    """Download Control Narratives."""
    logger.info("INIT: Downloading Control Narratives.")

    documents_list = await fetch_file_via_adapter(
        "",
        _CONFIG["documents_list_json_path"]
    )
    control_narratives_list = [
        doc for doc in documents_list if doc["type"] == "CONTROL NARRATIVE"
    ]

    for i, control_narrative in enumerate(control_narratives_list):
        narrative_num = f"{i + 1}/{len(control_narratives_list)}"
        narrative_name = control_narrative['name']
        logger.info(f"Downloading Narrative {narrative_num}")
        logger.info(f"Narrative Name: {narrative_name}")
        if control_narrative["status"] != "GENERATED":
            logger.info(
                f"""Control Narrative is not available for {narrative_name}.
                Skipping downloading Control Narrative."""
            )
            continue
        narrative_s3_key = (
            f"""public/{_CONFIG['plant_id']}/DOCS/CONTROL_NARRATIVE/{control_narrative['id']}/{
                control_narrative['id']}.CONTROL_NARRATIVE.inst.adm.json"""
        )
        length = len(control_narratives_list)
        logger.info(
            f"Downloading Control Narrative instruments{i + 1}/{length}: {narrative_name}"
        )
        narrative_data = await fetch_file_via_adapter(
            os.environ["BUCKET"],
            narrative_s3_key
        )
        narrative_local_path = (
            f"{_CONFIG['control_narratives_folder_path']}/{control_narrative['id']}"
            + ".cnd.inst.adm.json"
        )
        await upload_file_to_storage("", narrative_local_path, narrative_data)
        narrative_s3_key = (
            f"""public/{_CONFIG['plant_id']}/DOCS/CONTROL_NARRATIVE/{control_narrative['id']}/{
                control_narrative['id']}.CONTROL_NARRATIVE.cl.adm.json"""
        )
        length = len(control_narratives_list)
        logger.info(
            f"Downloading Control Narrative control loop{i + 1}/{length}: {narrative_name}"
        )
        narrative_data = await fetch_file_via_adapter(
            os.environ["BUCKET"],
            narrative_s3_key
        )
        narrative_local_path = (
            f"{_CONFIG['control_narratives_folder_path']}/{control_narrative['id']}"
            + ".cnd.cl.adm.json"
        )
        await upload_file_to_storage("", narrative_local_path, narrative_data)
    logger.info("DONE: Downloading Control Narratives.")


if __name__ == "__main__":
    asyncio.run(download_control_narrative())
