"""Local Script: Download Documents List."""

import json


from src.app import lambda_handler
from src.constants.Actions import Actions
from src.utils.disc_utils import read_json
from src.utils.log import logger

_CONFIG = read_json("data/configs/config.json")


def _get_event_payload():
    """This function returns event payload."""
    action = Actions.GET_LIST_OF_DOCUMENTS
    return {
        "body": {
            "action": action,
            "plant_id": _CONFIG["plant_id"],
            # "type": "DATA_SHEET",
        }
    }


async def download_document_list():
    """."""
    logger.info("INIT: download_document_list")
    logger.info(f"_CONFIG = \n{json.dumps(_CONFIG, indent=4)}")
    documents = await lambda_handler(_get_event_payload(), request="")["data"]
    documents_list_json_path = _CONFIG["documents_list_json_path"]
    with open(documents_list_json_path, "w", encoding="UTF-8") as f:
        json.dump(documents, f, indent=4)
    logger.info(f"Documents list saved at: {documents_list_json_path}")
    logger.info("DONE: download_document_list")


if __name__ == "__main__":
    download_document_list()
