"""This module contains functions to ingest HMB ADM"""
from src.app import lambda_handler
from src.utils.log import logger
from src.constants.Actions import Actions
from src.utils.disc_utils import read_dict_from_json

_CONFIG = read_dict_from_json("data/configs/config.json")


def get_event_payload():
    """This function returns event payload"""
    action = Actions.INGEST_PROCESS_NARRATIVE_ADM_INTO_NEO4J
    return {
        'body': {
            'action': action,
            'plant_id': _CONFIG["plant_id"],
            'data': 'data/sanha_staging/pnd_adms/SAN-PCP-10-032-01.pdf.pnd.adm.json'
        }
    }


async def ingest_pnd():
    """
    Function to process PND ADM ingestion.
    """
    try:
        event_payload = get_event_payload()
        print(event_payload)
        result = await lambda_handler(event_payload, request="")
        logger.info(f"Lambda function: ingest pnd adm, result: {result}")
    except (KeyError, IndexError, TypeError, ValueError) as error:
        logger.error(f"Error calling Lambda function: ingest pnd adm, error: {error}")


if __name__ == "__main__":
    ingest_pnd()
