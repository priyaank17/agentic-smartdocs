"""
Convert subpart data to subpart format.
"""

from src.data_sheets_v2.get_adm_json.get_nodes_folder.utils import (
    get_excluded_keys,
    tokenize,
    get_base_info,
)


def convert_to_subpart_format_final(entries):
    """Convert input entries into a structured
    subpart format with shell_side and tube_side details."""
    formatted_subpart_data = {"shell_side": [], "tube_side": [], "air_side": []}
    excluded_keys = get_excluded_keys()

    for entry in entries:
        shell_side_properties, tube_side_properties, air_side_properties = (
            extract_subpart_properties(
                entry,
                excluded_keys,
                {},
                {},
                {},
            )
        )

        base_metadata = get_base_info(entry)

        if shell_side_properties:
            shell_side_properties.update(base_metadata)
            formatted_subpart_data["shell_side"].append(shell_side_properties)

        if tube_side_properties:
            tube_side_properties.update(base_metadata)
            formatted_subpart_data["tube_side"].append(tube_side_properties)

        if air_side_properties:
            air_side_properties.update(base_metadata)
            formatted_subpart_data["air_side"].append(air_side_properties)
    return {"subparts": formatted_subpart_data}


def extract_subpart_properties(
    entry,
    excluded_keys,
    shell_side_properties,
    tube_side_properties,
    air_side_properties,
):
    """
    Extract properties relevant to the given flow direction ('shell_side' or 'tube_side').
    Categorize based on key names and applicable categories.
    """
    table_name = entry.get("table_name", "").lower()
    table_tokens = tokenize(table_name)
    for property_name, property_value in entry.items():
        if property_name in excluded_keys:
            continue

        property_tokens = tokenize(property_name)
        node_subpart_type = entry.get("node_subpart_type")
        if (
            "shell" in property_tokens or ("shell" and "side") in table_tokens
        ) and "shell_side" in node_subpart_type:  # or "shell" in table_tokens:
            shell_side_properties[property_name] = property_value
        elif (
            "tube" in property_tokens or ("tube" and "side") in table_tokens
        ) and "tube_side" in node_subpart_type:  # or "tube" in table_tokens:
            tube_side_properties[property_name] = property_value
        elif (
            "air" in property_tokens or ("air" and "side") in table_tokens
        ) and "air_side" in node_subpart_type:  # or "air" in table_tokens:
            air_side_properties[property_name] = property_value
        else:
            if "shell_side" in node_subpart_type:
                shell_side_properties[f"{property_name} shell side"] = property_value
            if "tube_side" in node_subpart_type:
                tube_side_properties[f"{property_name} tube side"] = property_value
            if "air_side" in node_subpart_type:
                air_side_properties[f"{property_name} air side"] = property_value
    return shell_side_properties, tube_side_properties, air_side_properties
