"""
This module is used for generating control narrative ADM from control narrative."""

import datetime
from src.utils.log import logger


def get_control_narrative_control_loops_adm(
    control_loop_adm_json_data, control_loop_data, document_id
):
    """Get control narrative adm"""
    logger.info("INIT: get control narrative control loop adm function initialized")
    control_loop_filter_data = get_control_loop_adm_data(control_loop_data)
    add_control_loop_data(control_loop_adm_json_data, control_loop_filter_data)
    add_meta_data(control_loop_adm_json_data, document_id)
    logger.info("DONE: get control narrative control loop adm function executed")
    return control_loop_adm_json_data


def get_control_loop_adm_data(data):
    """Control loop adm data"""
    control_loop_adm_data = []

    for item in data:
        equipment_name = item.get("equipment_name", "")
        transmitter_tags = list(item.get("transmitter", {}).keys())
        controller_tags = list(item.get("controller", {}).keys())
        control_valve_tags = list(item.get("control_valve", {}).keys())

        if transmitter_tags or controller_tags or control_valve_tags:
            control_loop_adm_item = {
                "transmitter": transmitter_tags,
                "controller": controller_tags,
                "control_valve": control_valve_tags,
                "equipment_name": equipment_name,
            }
            control_loop_adm_data.append(control_loop_adm_item)

    return control_loop_adm_data


def add_control_loop_data(json_data, control_loop_filter_data):
    """Add control_loop data"""
    logger.info("INIT: add control_loop data function initialized")
    add_control_loop_id(control_loop_filter_data)
    json_data["data"].extend(control_loop_filter_data)
    logger.info("DONE: add control_loop data function executed")


def add_control_loop_id(json_data):
    """Add id to json data"""
    i = 1
    # "control_loop_id"
    for control_loop in json_data:
        new_id = "control_loop_" + str(i)
        i = i + 1
        control_loop["id"] = new_id


def add_meta_data(json_data, document_id):
    """Add meta data to json data"""
    logger.info("INIT: add meta data function initialized")
    meta_data = {
        "uuid": document_id,
        "adm_version": "ADM_CONTROL_NARRATIVE_"
        + datetime.datetime.now().strftime("%Y-%m-%d"),
        "adm_generation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "adm_type": "CONTROL_NARRATIVE",
    }
    json_data["meta_data"] = meta_data
    logger.info("DONE: add meta data function executed")


def get_control_narrative_instrument_adm(
    json_data, control_narrative_instrument, document_id
):
    """Get control narrative adm"""
    logger.info("INIT: get control narrative instrument adm function initialized")
    add_control_instrument_data(json_data, control_narrative_instrument)
    add_meta_data(json_data, document_id)
    logger.info("DONE: get control narrative instrument adm function executed")
    return json_data


def add_control_instrument_data(json_data, control_narrative_instrument):
    """Add control_narrative instrument data"""
    logger.info("INIT: add control_narrative instrument data function initialized")
    add_control_narrative_instrument_id(control_narrative_instrument)
    json_data["data"].extend(control_narrative_instrument)
    logger.info("DONE: add control_narrative instrument data function executed")


def add_control_narrative_instrument_id(json_data):
    """Add id to json data"""
    i = 1
    for control_loop in json_data:
        new_id = "control_narrative_instrument_" + str(i)
        i = i + 1
        control_loop["id"] = new_id
