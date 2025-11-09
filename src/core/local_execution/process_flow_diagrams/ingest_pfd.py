"""This module ingests the Process Flow Diagrams (PFD) ADMs"""
from src.app import lambda_handler
from src.utils.log import logger
from src.constants.Actions import Actions
from src.utils.disc_utils import read_dict_from_json

_CONFIG = read_dict_from_json("data/configs/config.json")


def get_event_payload():
    """This function returns event payload"""
    action = Actions.INGEST_PFD_INTO_NEO4J
    return {
        'body': {
            'action': action,
            'plant_id': _CONFIG["plant_id"],
            'adm_path': _CONFIG["process_flow_diagrams_adm_path"]
        }
    }


async def ingest_hmb():
    """
    Function to process HMB ADM ingestion.
    """
    try:
        event_payload = get_event_payload()
        print(event_payload)
        result = await lambda_handler(event_payload, request="")
        logger.info(f"Lambda function: ingest pfd adm, result: {result}")
    except (KeyError, IndexError, TypeError, ValueError) as error:
        logger.error(f"Error calling Lambda function: ingest pfd adm, error: {error}")


if __name__ == "__main__":
    ingest_hmb()
