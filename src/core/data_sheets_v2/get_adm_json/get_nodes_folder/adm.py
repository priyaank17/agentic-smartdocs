"""Convert raw json data to adm format."""

# import json
from src.data_sheets_v2.get_adm_json.get_nodes_folder.utils import (
    get_excluded_keys,
    tokenize,
)
from src.data_sheets_v2.get_adm_json.get_nodes_folder.nozzle import (
    convert_to_nozzle_format_final,
)
from src.data_sheets_v2.get_adm_json.get_nodes_folder.subpart import (
    convert_to_subpart_format_final,
)
from src.data_sheets_v2.get_adm_json.get_nodes_folder.nodes import (
    convert_to_format_final,
)
from src.data_sheets_v2.get_adm_json.get_uuid import (
    add_uuid,
    add_data_sheet_uuid,
    add_equipment_uuid,
    add_subpart_uuid,
)
from src.data_sheets_v2.get_adm_json.get_meta_data.extract import get_metadata
from src.data_sheets_v2.get_adm_json.post_process import (
    convert_keys_to_camel_case,
    generate_relationships,
    ensure_all_entities_present,
    clean_uuid,
)
from src.data_sheets_v2.get_adm_json.get_nodes_folder.extract import (
    get_node_data,
)
from src.data_sheets_v2.get_adm_json.get_nodes_folder.flatten_adm import (
    flatten_json,
    patch_missing_equipments,
)
from src.utils.log import logger


def _get_side_from_tokens(key_tokens, table_tokens):
    """Get side from tokens."""
    if "shell" in key_tokens or ("shell" in table_tokens and "side" in table_tokens):
        return "shell"
    if "air" in key_tokens or ("air" in table_tokens and "side" in table_tokens):
        return "air"
    if "tube" in key_tokens or ("tube" in table_tokens and "side" in table_tokens):
        return "tube"
    return "UNKNOWN"


def _nozzle_node_to_adm(formatted_nozzle_data):
    """Filter out nozzle entries that are also categorized as subpart."""
    mpp = {}
    nozzle_number = 1

    for stream in ["inlet", "outlet"]:
        entries = formatted_nozzle_data.get(stream, [])
        for entry in entries:
            node_category = entry.get("node_category", [])
            if node_category:
                node_category = node_category[0].lower()
            else:
                node_category = ""
            standard_property = entry.get("Standard Property", "").strip().lower()
            table_name = entry.get("table_name", "").lower()
            table_tokens = tokenize(table_name)
            excluded_keys = get_excluded_keys()
            for key, value in entry.items():
                if key in excluded_keys:
                    continue
                key_tokens = tokenize(key)
                # side = None
                side = _get_side_from_tokens(key_tokens, table_tokens)
                if side:
                    side_key = f"{side} side {stream} {node_category}"
                    if side_key not in mpp:
                        mpp[side_key] = {}
                        mpp[side_key]["connection_type"] = stream.upper()
                        mpp[side_key]["subpart_name"] = f"{side.upper()}_SIDE"
                        mpp[side_key]["equipment_type_name"] = node_category
                        mpp[side_key][
                            "nozzle_number"
                        ] = f"UNNAMED_NOZZLE_{nozzle_number}"  # nozzle_number
                        nozzle_number += 1
                    mpp[side_key][standard_property] = value

    return {"nozzles": list(mpp.values())}


def _subpart_node_to_adm(formatted_subpart_data):
    """Convert subpart data to adm format."""

    mpp = {}
    for s in ["shell_side", "tube_side", "air_side"]:
        entries = formatted_subpart_data.get(s, [])
        for entry in entries:
            standard_property = entry.get("Standard Property", "").strip().lower()
            table_name = entry.get("table_name", "").lower()
            node_category = entry.get("node_category", [])
            if node_category:
                node_category = node_category[0].lower()
            else:
                node_category = ""
            table_tokens = tokenize(table_name)
            excluded_keys = get_excluded_keys()
            for key, value in entry.items():
                if key in excluded_keys:
                    continue
                key_tokens = tokenize(key)
                side = _get_side_from_tokens(key_tokens, table_tokens)
                if side:
                    side_key = f"{side} side"
                    if side_key not in mpp:
                        mpp[side_key] = {}
                        mpp[side_key]["subpart_name"] = f"{side.upper()}_SIDE"
                        mpp[side_key]["equipment_type_name"] = node_category
                    mpp[side_key][standard_property] = value

    return {"subparts": list(mpp.values())}


def _add_property_to_adm_mapping(adm_mapping, node_entries_info, key, value):
    node_key = node_entries_info.get("node_key")
    standard_property = node_entries_info.get("standard_property")
    node_category = node_entries_info.get("node_category")
    node_subparts = node_entries_info.get("node_subpart_type")
    key_tokens = tokenize(key)
    node_tokens = tokenize(node_key)

    excluded_keys = get_excluded_keys()

    if key in excluded_keys or node_tokens.isdisjoint(key_tokens):
        return

    if node_subparts:
        for subpart in node_subparts:
            subpart_tokens = tokenize(subpart)
            if not subpart_tokens.isdisjoint(key_tokens):
                subpart_dict = adm_mapping[node_key][node_category].setdefault(
                    subpart, {}
                )
                subpart_dict[standard_property] = value
    else:
        adm_mapping[node_key][node_category][standard_property] = value


def _equipment_and_other_node_to_adm(formatted_equipment_and_other_data):
    """
    Convert equipment/subpart data to ADM format.
    Groups properties by node, category, and optionally subpart type.
    """
    adm_mapping = {}

    for node_key, entries in formatted_equipment_and_other_data.items():
        for entry in entries:
            standard_property = entry.get("Standard Property", "")
            if not standard_property:
                logger.warning(
                    f"Standard Property not found for node: {node_key}, entry: {entry}"
                )
                continue
            node_category = entry.get("node_category", [])[0]
            node_entries_info = {
                "node_key": node_key,
                "standard_property": standard_property.strip().lower(),
                "node_category": node_category,
                "node_subpart_type": entry.get("node_subpart_type", []),
            }

            if node_key not in adm_mapping:
                adm_mapping[node_key] = {}
            if node_category not in adm_mapping[node_key]:
                adm_mapping[node_key][node_category] = {}

            for key, value in entry.items():
                _add_property_to_adm_mapping(adm_mapping, node_entries_info, key, value)

    return adm_mapping


def _process_nozzle_data(processed_data):
    """Process nozzle data and convert to ADM format."""
    nozzle_processed_data = processed_data.get("nozzles", [])
    if not nozzle_processed_data:
        return {"nozzles": []}

    nozzle_data = convert_to_nozzle_format_final(nozzle_processed_data)
    nozzle_adm = _nozzle_node_to_adm(nozzle_data.get("nozzles", {}))
    return nozzle_adm


def _process_subpart_data(processed_data):
    """Process subpart data and convert to ADM format."""
    subpart_processed_data = processed_data.get("subparts", [])
    if not subpart_processed_data:
        return {"subparts": []}

    subpart_data = convert_to_subpart_format_final(subpart_processed_data)
    subpart_adm = _subpart_node_to_adm(subpart_data.get("subparts", {}))

    return subpart_adm


def _process_equipment_and_other_nodes(processed_data):
    """Process equipment and other nodes data and convert to ADM format."""
    equipment_data = convert_to_format_final(processed_data)
    equipment_adm = _equipment_and_other_node_to_adm(equipment_data)
    return equipment_adm


def _flatten_standard_tables(adm):
    """
    Flatten standard tables into a list of tables and a list of entries.
    """
    standard_tables = []
    standard_table_entries = []

    if "standard_tables" in adm and isinstance(adm["standard_tables"], dict):
        for node_name, tables in adm["standard_tables"].items():
            print(node_name)
            if node_name in ["equipment_tag", "uuid", "data_sheet_uuid"]:
                continue
            for table_name, table_data in tables.items():
                # Create the new StandardTable node
                table_node = {
                    "tableName": table_name,
                    "nodeName": node_name,
                    "entries": [],
                }

                # Create and link the StandardTableEntry nodes
                for entry_data in table_data:
                    entry_node = {
                        **entry_data,
                        "table_name": table_name,
                    }
                    table_node["entries"].append(entry_node)
                    standard_table_entries.append(entry_node)

                standard_tables.append(table_node)

    adm["standard_tables"] = standard_tables
    adm["standard_table_entries"] = standard_table_entries
    return adm


async def get_adm_json(raw_data, document_id, standard_mapping_df):
    """Convert data_sheet JSON to ADM format."""
    logger.info("INIT: get_adm_json")
    processed_data = get_node_data(raw_data, standard_mapping_df)
    meta_data = get_metadata(raw_data)
    nozzle_node_adm = _process_nozzle_data(processed_data)
    subpart_node_adm = _process_subpart_data(processed_data)
    equipment_and_other_node_adm = _process_equipment_and_other_nodes(processed_data)
    flatter_equipment_and_other_node_adm = flatten_json(equipment_and_other_node_adm)
    adm = {"meta_data": meta_data, **flatter_equipment_and_other_node_adm}
    equipment_tag = meta_data["equipment_tag"]

    if nozzle_node_adm:
        adm.update(nozzle_node_adm)

    if subpart_node_adm:
        adm.update(subpart_node_adm)

    # Process non-standard data and merge it into the ADM
    # non_standard_adm = get_non_standard_adm_json(raw_data)

    # # Ensure standard_tables key exists
    # if "standard_tables" not in adm:
    #     adm["standard_tables"] = {}

    # for node_name, node_content in non_standard_adm.items():
    #     # Ensure 'tables' key exists in node_content
    #     if "tables" not in node_content:
    #         continue  # skip if nothing to merge

    #     # Ensure the node bucket exists under standard_tables
    #     if node_name not in adm["standard_tables"]:
    #         adm["standard_tables"][node_name] = {}

    #     # Merge each table inside that node
    #     for table_name, table_data in node_content["tables"].items():
    #         if table_name in adm["standard_tables"][node_name]:
    #             # Merge by extending existing table rows
    #             adm["standard_tables"][node_name][table_name].extend(table_data)
    #         else:
    #             # New table entirely
    #             adm["standard_tables"][node_name][table_name] = table_data

    updated_adm = patch_missing_equipments(adm)
    output_adm_json = _get_adm_json_with_uuid(updated_adm, document_id, equipment_tag)
    # output_adm_json = _flatten_standard_tables(output_adm_json)
    # output_adm_json = add_standard_table_uuid(output_adm_json)
    # output_adm_json = add_standard_table_entry_uuid(output_adm_json)
    output_json_camel_case = convert_keys_to_camel_case(output_adm_json)
    with_relationships_node = generate_relationships(output_json_camel_case)

    output_json_camel_case["entityToEntityRelationships"] = with_relationships_node
    clean_uuid(output_json_camel_case)
    output_json_camel_case = ensure_all_entities_present(output_json_camel_case)
    length = len(output_json_camel_case)
    if length != 19:
        print(
            f"Warning: The ADM data does not contain all required entities. Length: {length}"
        )
    logger.info("DONE: get_adm_json")

    return output_json_camel_case


def _get_adm_json_with_uuid(adm, document_id, equipment_tag):
    """Add UUID to the ADM data."""
    final_adm = add_uuid(adm, document_id, equipment_tag)
    output_adm_json = add_data_sheet_uuid(final_adm)
    output_adm_json = add_equipment_uuid(output_adm_json)
    output_adm_json = add_subpart_uuid(output_adm_json)
    return output_adm_json
