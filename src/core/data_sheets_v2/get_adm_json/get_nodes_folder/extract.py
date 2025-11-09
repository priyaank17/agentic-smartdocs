"""
This module is used to extract nodes from JSON input."""

import json
import re
from fuzzywuzzy import process
from src.utils.llm_models.get_llm import get_llm_model
from src.utils.log import logger
from src.data_sheets_v2.get_adm_json.get_nodes_folder.get_prompt_nodes import (
    get_nodes_column_prompt,
)
from src.data_sheets_v2.get_adm_json.get_nodes_folder.utils import (
    get_nodes_to_extract,
)


def get_fuzzy_matches(standard_key, standard_nodes_df):
    """Get fuzzy matches for the standard key in the standard nodes DataFrame."""
    keys = list(standard_nodes_df.keys())
    # Get the best matches using fuzzy matching
    normalized_standard_key = standard_key.replace("_", " ").lower()
    normalized_keys = [key.replace("_", " ").lower() for key in keys]
    # matches = process.extract(normalized_standard_key, normalized_keys, limit=5)
    best_match = process.extractOne(normalized_standard_key, normalized_keys)
    best_match_name = best_match[0]

    if best_match[1] > 0.8:
        best_match_name = best_match_name.replace(" ", "_").lower()
        return best_match_name

    logger.warning(f"No fuzzy matches found for standard key: {standard_key}")
    return None


def get_nodes_details_llm(llm_input):
    """Extract nodes data from JSON input."""
    logger.info("INIT: Extracting node data from JSON input using LLM")
    table_name = llm_input.get("table_name", "").strip().lower()
    parent_table_name = llm_input.get("parent_table_name", "").strip().lower()
    node_entity = get_nodes_to_extract()

    llm = get_llm_model(model_name="gpt-4o")
    message = get_nodes_column_prompt(table_name, parent_table_name, node_entity)
    response = llm.invoke(message)
    extracted_output = response.content

    logger.info("DONE: Extracting nodes data from JSON input")
    return extracted_output


def extract_json_from_text(text: str) -> dict:
    """
    Extracts a JSON block enclosed in ```json ... ``` from the given text.
    """
    match = re.search(r"```json\s+(.*?)```", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON block found in the input.")

    json_str = match.group(1).strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}") from e


def get_correct_standard_property_data(
    node_entries, row_parent_table_name, row_table_name
):
    """Get correct standard property data."""
    for node_entry in node_entries:
        parent_table_list = node_entry.get("parent_table_name", [])
        possible_table_list = node_entry.get("possible_table_name", [])
        if parent_table_list:
            parent_table_list = [pt.strip().lower() for pt in parent_table_list]

        possible_table_list = [pt.strip().lower() for pt in possible_table_list]

        if row_parent_table_name and row_parent_table_name.lower() in parent_table_list:
            node_name = node_entry.get("node_name")
            node_category = node_entry.get("node_category")
            node_subpart_type = node_entry.get("node_subpart_type")
            return {
                "node_name": node_name,
                "node_category": node_category,
                "node_subpart_type": node_subpart_type,
            }
        if row_table_name and row_table_name.lower() in possible_table_list:
            node_name = node_entry.get("node_name")
            node_category = node_entry.get("node_category")
            node_subpart_type = node_entry.get("node_subpart_type")
            return {
                "node_name": node_name,
                "node_category": node_category,
                "node_subpart_type": node_subpart_type,
            }
    logger.warning("No matching node entry found")
    return None


def log_node_warnings(node_name, standard_key):
    """
    Log warnings for node extraction issues.
    """
    if not node_name:
        logger.warning(
            f"No node name found for standard key '{standard_key}';"
            "check the standard_nodes_df."
        )
    elif len(node_name) > 1:
        logger.warning(
            "Multiple node names found for standard key "
            f"{standard_key}: {node_name}. Using the first one."
        )


def process_rows(
    row_data_info,
    table_data,
    output_json,
):
    """
    Process rows of the table data and populate the output JSON.
    """
    for row in table_data:
        row["table_name"] = row_data_info["table_name"]
        row["parent_table_name"] = row_data_info["parent_table_name"]
        row["node_category"] = row_data_info["node_category"]
        row["node_name"] = [row_data_info["node_name"][0]]
        row["node_subpart_type"] = extract_node_category(
            row["node_name"],
            row_data_info["node_category"],
            row_data_info["node_subpart_type"],
        )

        if row["node_name"][0] not in output_json:
            output_json[row["node_name"][0]] = []
        output_json[row["node_name"][0]].append(row)


def get_node_data(raw_json, standard_nodes_df):
    """Get node data from JSON input."""
    logger.info("INIT: Getting nodes data from JSON input")
    output_json = {}
    for table in raw_json:
        if not isinstance(table, dict):
            logger.info("Skipping table: Must be a dictionary.")
            continue
        if (
            not table.get("column_names")
            or not isinstance(table.get("column_names"), list)
            or "standard_property"
            not in [
                col.strip().lower().replace(" ", "_")
                for col in table.get("column_names", [])
            ]
        ):
            logger.info(
                "Skipping table: Must have a 'column_names' key with value 'Standard Property'."
            )
            continue

        table_name = (table.get("table_name") or "").strip().lower()
        if not table_name:
            logger.warning("Missing table name in input")
            continue
        parent_table_name = (
            (table.get("parent_table_name") or "").strip().lower().replace(" ", "_")
        )
        standard_key = table_name.replace(" ", "_")
        if parent_table_name:
            standard_key = f"{standard_key}_{parent_table_name}"

        logger.info(f"Processing table: {table_name} with standard key: {standard_key}")
        extracted_table_data = table.get("data", [])

        if standard_key in standard_nodes_df:
            logger.info(f"Found direct match for standard key: {standard_key}")
            nodes_data = standard_nodes_df[standard_key][0]
        else:
            logger.warning(
                f"Standard key {standard_key} not found in standard_nodes_df"
            )
            best_fuzzy_match_name = get_fuzzy_matches(standard_key, standard_nodes_df)

            if best_fuzzy_match_name:
                logger.info(
                    "Using best fuzzy matches for"
                    f"standard key {standard_key}: {best_fuzzy_match_name}"
                )
                nodes_data = standard_nodes_df[best_fuzzy_match_name][0]
            else:
                logger.info(
                    f"Using LLM to extract nodes for standard key {standard_key}"
                )
                llm_input = {
                    "table_name": table_name,
                    "parent_table_name": parent_table_name,
                }

                extracted_node_data = get_nodes_details_llm(llm_input)
                result = extract_json_from_text(extracted_node_data)
                print("result", result)
                node_name = (
                    [result.get("node_name", "others")] if result else ["others"]
                )
                node_category = (
                    [result.get("node_category", "auxiliary_equipments")]
                    if result
                    else ["auxiliary_equipments"]
                )
                node_subpart_type = (
                    [result.get("node_subpart_type", "others")]
                    if result
                    else ["others"]
                )
                row_data_info = {
                    "table_name": table_name,
                    "parent_table_name": parent_table_name,
                    "node_name": node_name,
                    "node_category": node_category,
                    "node_subpart_type": node_subpart_type,
                }
                log_node_warnings(node_name, standard_key)
                process_rows(
                    row_data_info,
                    extracted_table_data,
                    output_json,
                )
                continue

        # Process row using nodes data from standard/fuzzy
        row_data_info = {
            "table_name": table_name,
            "parent_table_name": parent_table_name,
            "node_name": nodes_data["node_name"],
            "node_category": nodes_data["node_category"],
            "node_subpart_type": nodes_data["node_subpart_type"],
        }
        log_node_warnings(row_data_info["node_name"], standard_key)
        process_rows(
            row_data_info,
            extracted_table_data,
            output_json,
        )

    logger.info("DONE: Getting nodes data from JSON input")
    return output_json


def extract_node_category(node_name_list, node_category_list, node_subpart_type):
    """Extract applicable categories for nodes."""

    nodes_map = get_nodes_to_extract()
    matched_categories = []
    node_category = node_category_list[0]

    for node_name in node_name_list:
        if node_name in nodes_map:
            child_subpart_type_list = nodes_map[node_name][node_category]
            filtered_categories = [
                subpart_type
                for subpart_type in child_subpart_type_list
                if subpart_type in node_subpart_type
            ]
            matched_categories.extend(filtered_categories)
    return matched_categories
