"""Flattens the JSON structure of ADM data."""

from src.data_sheets_v2.get_adm_json.get_nodes_folder.utils import (
    get_nodes_to_extract,
)


def flatten_json(data):
    """
    Flattens the JSON structure of ADM data."""
    output = {}

    for section_key, section_val in data.items():
        section_list = []

        for eq_type, eq_val in section_val.items():
            if isinstance(eq_val, dict):
                for sub_key, sub_val in eq_val.items():
                    if isinstance(sub_val, dict):
                        # Sub-equipment like agitator under auxiliary_equipments
                        entry = sub_val.copy()
                        entry["equipment_type_name"] = eq_type
                        # f"{sub_key}_{eq_type}"
                        entry["subpart_type_name"] = sub_key

                        section_list.append(entry)
                    else:
                        # Flat properties under primary_equipments
                        entry = eq_val.copy()
                        entry["equipment_type_name"] = eq_type
                        entry["subpart_type_name"] = None
                        section_list.append(entry)
                        break  # Only add once
            else:
                # Flat section like revisions
                entry = section_val.copy()
                entry["equipment_type_name"] = eq_type
                entry["subpart_type_name"] = None
                section_list.append(entry)
                break

        output[section_key] = section_list

    return output


def patch_missing_equipments(adm_json) -> dict:
    """
    Ensures all unique (equipment_type_name, subpart_type_name) pairs from the document
    are present in the 'equipments' list. Adds missing ones.
    """
    nodes_to_extract = get_nodes_to_extract()
    sections_to_check = list(nodes_to_extract.keys())

    # Collect all unique (equipment_type_name, subpart_type_name) pairs
    unique_pairs = set()
    for section in sections_to_check:
        for item in adm_json.get(section, []):
            eq_type = item.get("equipment_type_name")
            sub_type = item.get("subpart_type_name")
            if eq_type:
                unique_pairs.add((eq_type, sub_type))

    # Get current pairs in the equipments list
    existing_pairs = set()
    for eq in adm_json.get("equipments", []):
        existing_pairs.add((eq.get("equipment_type_name"), eq.get("subpart_type_name")))

    # Determine which pairs are missing
    missing_pairs = unique_pairs - existing_pairs

    # Add missing pairs to the equipments list
    for eq_type, sub_type in missing_pairs:
        adm_json.setdefault("equipments", []).append(
            {"equipment_type_name": eq_type, "subpart_type_name": sub_type}
        )

    return adm_json
