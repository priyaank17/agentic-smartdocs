"""
This module is used for generating process narrative ADM from process narrative."""

import datetime
from src.utils.log import logger


def get_process_narrative_adm(json_data, equipment_data, document_id):
    """Get process narrative adm"""
    logger.info("INIT: get process narrative adm function initialized")
    add_equipment_data(json_data, equipment_data)
    add_meta_data(json_data, document_id)
    logger.info("DONE: get process narrative adm function executed")
    return json_data


def add_equipment_data(json_data, equipment_data):
    """Add equipment data"""
    logger.info("INIT: add equipment data function initialized")
    add_equipment_id(equipment_data)
    json_data["data"].extend(equipment_data)
    logger.info("DONE: add equipment data function executed")


def add_equipment_id(json_data):
    """Add id to json data"""
    i = 1
    for equipment in json_data:
        new_id = "equipment_" + str(i)
        i = i + 1
        equipment["id"] = new_id


def add_meta_data(json_data, document_id):
    """Add meta data to json data"""
    logger.info("INIT: add meta data function initialized")
    meta_data = {
        "uuid": document_id,
        "adm_version": "ADM_PROCESS_NARRATIVE_" + datetime.datetime.now().strftime("%Y-%m-%d"),
        "adm_generation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "adm_type": "PROCESS_NARRATIVE"
    }
    json_data["meta_data"] = meta_data
    logger.info("DONE: add meta data function executed")
