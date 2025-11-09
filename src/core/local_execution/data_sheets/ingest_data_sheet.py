"""This module is responsible for ingesting data sheets."""

from py_unified_cloud_adapter.utils.errors import CloudAdapterException
from src.utils.log import logger
from src.app import lambda_handler
from src.constants.Actions import Actions
from src.utils.disc_utils import read_dict_from_json

_CONFIG = read_dict_from_json("data/configs/config.json")


def get_event_payload():
    """function to get event payload"""
    action = Actions.INGEST_DATA_SHEET_ADM_INTO_NEO4J
    return {
        'body': {
            'action': action,
            'plant_id': _CONFIG["plant_id"],
            "adm_path": (
                "data/sanha_dev/data_sheets/"
                "SAN-PCP-MEC-DAS-CBA-2300-00.pdf.data_sheet.adm.json"
            ),
            # "adm_path": (
            #     "public/44bbbac3-f496-4a6c-800e-808e1dec1fe8/DOCS/data_sheet/"
            #     "ddcc8dfb-ac73-462e-b2c6-bfee4c8f07b7.datasheet.adm.json"
            # ),
        }
    }


async def ingest_data_sheet():
    """
    Function to process Data Sheet ADM ingestion.
    """
    try:
        event_payload = get_event_payload()
        print(event_payload)
        result = await lambda_handler(event_payload, request="")
        logger.info(f"Lambda function: ingest data sheet adm, result: {result}")
    except CloudAdapterException as error:
        logger.error(f"Error calling Lambda function: ingest adm, error: {error}")


if __name__ == "__main__":
    ingest_data_sheet()
