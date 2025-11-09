"""
Convert subpart data to subpart format.
"""

from src.data_sheets_v2.get_adm_json.get_nodes_folder.utils import (
    get_excluded_keys,
    get_base_info,
)


def convert_to_format_final(data):
    """Convert input entries into a structured subpart format details."""
    output_json = {}
    for entries in data:
        if entries == "subparts":
            continue
        if entries == "nozzles":
            continue
        if entries == "meta_data":
            continue
        excluded_keys = get_excluded_keys()
        formatted_data = []

        for entry in data[entries]:
            properties = extract_properties(
                entry,
                excluded_keys,
                {},
            )

            base_metadata = get_base_info(entry)

            if properties:
                properties.update(base_metadata)
                formatted_data.append(properties)
        if formatted_data:
            output_json[entries] = formatted_data

    return output_json


def extract_properties(
    entry,
    excluded_keys,
    properties,
):
    """
    Extract properties relevant to the given flow direction
    Categorize based on key names and applicable categories.
    """
    for property_name, property_value in entry.items():
        if property_name in excluded_keys:
            continue

        node_name = entry.get("node_name")
        node_subpart_type = entry.get("node_subpart_type")
        if node_name and node_subpart_type:
            for node_subpart in node_subpart_type:
                properties[f"{property_name} {node_name[0]} {node_subpart}"] = property_value
        elif node_name:
            properties[f"{property_name} {node_name[0]}"] = property_value
        # else:
        #     node_subpart_type = entry.get("node_subpart_type", [])
        #     properties[f"{property_name} {node_subpart_type[0]}"] = property_value
    return properties
