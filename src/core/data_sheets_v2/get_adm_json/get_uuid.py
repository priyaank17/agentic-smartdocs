"""Add UUIDs to the input data."""

import uuid
from src.utils.log import logger
from src.data_sheets_v2.get_adm_json.get_nodes_folder.utils import (
    node_with_equipment_connect,
)


def add_uuid(data, document_id, equipment_tag):
    """
    Add UUIDs to the input data.
    """
    logger.info("INIT: Adding UUIDs to the input data")
    for key, value in data.items():
        # If it's a dictionary (like meta_data), add a UUID
        if key == "meta_data":
            value["uuid"] = document_id
            continue
        if isinstance(value, dict):
            value["equipment_tag"] = equipment_tag
            value["uuid"] = str(uuid.uuid4())
        # If it's a list, and the list contains dicts, add UUID to each dict
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    item["equipment_tag"] = equipment_tag
                    item["uuid"] = str(uuid.uuid4())
    logger.info("DONE: Adding UUIDs to the input data")
    return data


def add_data_sheet_uuid(data):
    """
    Add UUIDs to the input data.
    """
    logger.info("INIT: Adding document UUIDs to the input data")
    data_sheet_uuid = data.get("meta_data", {}).get("uuid", None)
    for key, value in data.items():
        # If it's a dictionary (like meta_data), add a UUID
        if key == "meta_data":
            continue
        if isinstance(value, dict):
            value["data_sheet_uuid"] = data_sheet_uuid
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    item["data_sheet_uuid"] = data_sheet_uuid
    logger.info("DONE: Adding data sheet UUIDs to the input data")
    return data


def add_subpart_uuid(data):
    """
    Efficiently add subpart UUIDs to the 'nozzles' based on matching 'subpart_name'.
    """
    logger.info("INIT: Adding subpart UUIDs to the input data")

    # Build a map from subpart_name to UUID for quick lookup
    subpart_name_to_uuid = {
        subpart.get("subpart_name"): subpart.get("uuid")
        for subpart in data.get("subparts", [])
        if "subpart_name" in subpart and "uuid" in subpart
    }
    # print("subpart_name_to_uuid", subpart_name_to_uuid)

    # Process 'nozzles' only
    nozzles = data.get("nozzles")
    if isinstance(nozzles, dict):
        subpart_name = nozzles.get("subpart_name")
        if subpart_name.lower() in subpart_name_to_uuid.lower():
            nozzles["subpart_uuid"] = subpart_name_to_uuid[subpart_name]

    elif isinstance(nozzles, list):
        for nozzle in nozzles:
            if isinstance(nozzle, dict):
                subpart_name = nozzle.get("subpart_name")
                if subpart_name in subpart_name_to_uuid:
                    nozzle["subpart_uuid"] = subpart_name_to_uuid[subpart_name]

    logger.info("DONE: Adding subpart UUIDs to the input data")
    return data


def add_equipment_uuid(data):
    """
    Efficiently add equipment UUIDs to 'nozzles' and 'sub_parts' based on 'equipment_tag'.
    """
    logger.info("INIT: Adding equipment UUIDs to the input data")

    # Step 1: Build a fast lookup from equipment_tag to UUID

    equipment_map = {}
    for eq in data.get("equipments", []):
        key = (
            eq.get("equipment_tag"),
            eq.get("equipment_type_name"),
            eq.get("subpart_type_name"),
        )
        equipment_map[key] = eq.get("uuid")
    # Step 2: Target relevant sections only
    sections = (
        node_with_equipment_connect
        if isinstance(node_with_equipment_connect, (list, tuple))
        else node_with_equipment_connect()
    )

    for section in sections:
        # print("current section", section)
        items = data.get(section)
        if not items:
            print(f"No items found in section: {section}")
            continue
        # print("items", items)
        for item in items:
            if isinstance(item, dict):
                key = (
                    item.get("equipment_tag"),
                    item.get("equipment_type_name"),
                    item.get("subpart_type_name"),
                )
                correct_uuid = equipment_map.get(key)
                if correct_uuid:
                    item["equipmentUuid"] = correct_uuid
                else:
                    logger.warning(f"Missing equipment UUID mapping for: {key}")

    logger.info("DONE: Adding equipment UUIDs to the input data")
    return data


# def add_standard_table_uuid(data):
#     """
#     Add UUIDs to standard tables.
#     """
#     logger.info("INIT: Adding standard table UUIDs")
#     # if "standard_tables" in data and isinstance(data["standard_tables"], list):
#     for table in data.get("standard_tables", []):
#         if isinstance(table, dict):
#             table["uuid"] = str(uuid.uuid4())
#     logger.info("DONE: Adding standard table UUIDs")
#     return data


# def add_standard_table_entry_uuid(data):
#     """
#     Add UUIDs to standard table entries.
#     """
#     logger.info("INIT: Adding standard table entry UUIDs")
#     # if "standard_table_entries" in data and isinstance(
#     #     data["standard_table_entries"], list
#     # ):
#     for entry in data.get("standard_table_entries", []):
#         if isinstance(entry, dict):
#             entry["uuid"] = str(uuid.uuid4())
#     logger.info("DONE: Adding standard table entry UUIDs")
#     return data
