"""
Convert nozzle data to nozzle format.
"""

from src.data_sheets_v2.get_adm_json.get_nodes_folder.utils import (
    get_excluded_keys,
    tokenize,
    get_base_info,
)


def convert_to_nozzle_format_final(entries):
    """Convert input entries into a structured nozzle format with inlet and outlet details."""
    formatted_nozzle_data = {"inlet": [], "outlet": []}
    excluded_keys = get_excluded_keys()

    for entry in entries:
        inlet_properties, outlet_properties = extract_nozzle_properties(
            entry,
            excluded_keys,
            {},
            {},
        )

        base_metadata = get_base_info(entry)

        if inlet_properties:
            inlet_properties.update(base_metadata)
            formatted_nozzle_data["inlet"].append(inlet_properties)

        if outlet_properties:
            outlet_properties.update(base_metadata)
            formatted_nozzle_data["outlet"].append(outlet_properties)

    # print("formatted_nozzle_data", formatted_nozzle_data)
    # with open("formatted_nozzle_data.json", "w", encoding="utf-8") as f:
    #     import json

    #     json.dump(formatted_nozzle_data, f, indent=2)
    return {"nozzles": formatted_nozzle_data}


def extract_nozzle_properties(
    entry, excluded_keys, inlet_properties, outlet_properties
):
    """
    Extract properties relevant to the given flow direction ('inlet' or 'outlet').
    Categorize based on key names and applicable categories.
    """
    # print(entry)
    # applicable_categories = entry.get("applicable_categories", [])
    # print("applicable_categories", applicable_categories)

    for property_name, property_value in entry.items():
        if property_name in excluded_keys:
            continue

        property_tokens = tokenize(property_name)
        node_subpart_type = entry.get("node_subpart_type")
        # print("nozzle node_subpart_type", node_subpart_type)

        if (
            "inlet" in property_tokens or "in" in property_tokens
        ) and "inlet" in node_subpart_type:
            inlet_properties[property_name] = property_value
        elif (
            "outlet" in property_tokens or "out" in property_tokens
        ) and "outlet" in node_subpart_type:
            outlet_properties[property_name] = property_value
        else:
            if "inlet" in node_subpart_type:
                inlet_properties[f"{property_name} inlet"] = property_value
            if "outlet" in node_subpart_type:
                outlet_properties[f"{property_name} outlet"] = property_value
    return inlet_properties, outlet_properties
