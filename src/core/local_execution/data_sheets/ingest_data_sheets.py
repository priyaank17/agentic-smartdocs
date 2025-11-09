"""This module is responsible for ingesting data sheets."""

import os
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rich_print
from src.app import lambda_handler
from src.utils.log import logger
from src.constants.Actions import Actions
from src.utils.disc_utils import read_dict_from_json

PROGRESS = {
    "progress": None,
    "task": None,
}
_CONFIG = read_dict_from_json("data/configs/config.json")


def get_event_payload(adm_path):
    """This function returns event payload"""
    action = Actions.INGEST_DATA_SHEET_ADM_INTO_NEO4J
    return {
        "body": {
            "action": action,
            "plant_id": _CONFIG["plant_id"],
            "adm_path": adm_path,
        }
    }


def _panel_log(message, title):
    rich_print(
        Panel(
            message,
            title=title,
            border_style="blue",
        )
    )
    PROGRESS["progress"].update(PROGRESS["task"], advance=1)


async def ingest_data_sheets():
    """This function ingests data sheets"""
    logger.info("INIT: Ingesting data sheets - LOCAL ENVIRONMENT")

    data_sheet_adms_folder_path = _CONFIG["data_sheet_adms_folder_path"]
    file_list = os.listdir(data_sheet_adms_folder_path)

    PROGRESS["task"] = PROGRESS["progress"].add_task(
        "[blue]Ingesting...", total=len(file_list)
    )
    for i, file_name in enumerate(file_list, start=1):
        _panel_log(
            message=f"Ingesting file {file_name}",
            title=f"Data Sheet Ingestion {i}/{len(file_list)}",
        )

        adm_path = os.path.join(data_sheet_adms_folder_path, file_name)
        event_payload = get_event_payload(adm_path)
        await lambda_handler(event_payload, request="")

    logger.info("DONE: Ingesting data sheets - LOCAL ENVIRONMENT")


if __name__ == "__main__":
    with Progress() as PROGRESS["progress"]:
        ingest_data_sheets()
