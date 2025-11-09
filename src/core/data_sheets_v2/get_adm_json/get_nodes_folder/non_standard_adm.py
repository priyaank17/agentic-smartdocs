"""Script to get non-standard ADM JSON data from raw JSON."""

import re
from src.utils.llm_models.get_llm import get_llm_model


def to_snake_case(text):
    """Convert a string to snake_case."""
    # Convert strings like "REV" or "in NPS" to "rev" or "in_nps"
    text = re.sub(r"[\s\-]+", "_", text)  # Replace spaces or hyphens with underscores
    text = re.sub(
        r"(?<=[a-z0-9])(?=[A-Z])", "_", text
    )  # Add underscore before camelCase capitals
    return text.lower()


def convert_keys_and_columns(obj):
    """Recursively convert keys and column names in a dictionary or list to snake_case."""
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_key = to_snake_case(k)
            # Handle column_names separately
            if new_key == "column_names" and isinstance(v, list):
                new_obj[new_key] = [to_snake_case(col) for col in v]
            else:
                new_obj[new_key] = convert_keys_and_columns(v)
        return new_obj
    if isinstance(obj, list):
        return [convert_keys_and_columns(item) for item in obj]
    return obj


def get_raw_non_standard_adm_json(raw_json):
    """
    Function to get non-standard ADM JSON data from raw JSON.
    """
    output_json = {}
    # Count occurrences to know if we need to append appearance_number
    table_name_counts = {}
    for t in raw_json:
        name = t.get("table_name", "").strip().lower()
        if name:
            table_name_counts[name] = table_name_counts.get(name, 0) + 1

    for table in raw_json:
        table_name = table.get("table_name")
        if not table_name:
            continue
        table_name = table_name.strip().lower()

        unique_table_name = table_name
        # If the table appears more than once, create a unique name with appearance_number
        if table_name_counts.get(table_name, 1) > 1:
            appearance_number = table.get("appearance_number")
            if appearance_number is not None:
                unique_table_name = f"{table_name}{appearance_number}"

        parent_table_name = table.get("parent_table_name", "").strip().lower()
        data = table.get("data")
        column_names = table.get("column_names", [])

        if "Standard Property" in column_names:
            continue

        output_json[unique_table_name] = {
            "data": data,
            "column_names": column_names,
            "parent_table_name": parent_table_name,
            "original_table_name": table_name
        }
    return output_json


def get_node_name_from_llm(table_name, parent_table_name):
    """
    Use an LLM to get the node name for a non-standard table.
    """
    llm = get_llm_model(model_name="gpt-4o")
    node_names = [
        "meta_data",
        "nozzles",
        "subparts",
        "equipments",
        "operating_conditions",
        "performance",
        "mechanical_geometry",
        "instrumentation",
        "notes",
        "heat_curves",
        "revisions",
        "process_fluids",
        "testing_inspections",
        "materials",
        "construction_accessories",
        "driver_motor",
        "design_conditions",
        "others",
    ]
    prompt = f'''
    Given the following table name and parent table name, which of the following node names does the table belong to? Respond with only the single most relevant node name from the list.

    Table Name: {table_name}
    Parent Table Name: {parent_table_name}

    Node Names: {node_names}

    If you are not sure, or if the table does not fit into any of the categories, please respond with "others".
    '''
    response = llm.invoke(prompt)
    node_name = response.content.strip().lower().replace(" ", "_")

    if node_name not in node_names:
        node_name = "others"

    return node_name


def convert_table_to_json(data, column_names):
    """
    Convert table data to a list of JSON objects.
    """
    json_data = []
    for row in data:
        json_row = {}
        # Check if the row is a dictionary
        if not isinstance(row, dict):
            # if not a dictionary, assume it is a list of values in order of column_names
            for i, col in enumerate(column_names):
                try:
                    json_row[col] = row[i]
                except IndexError:
                    json_row[col] = None  # or some default value
        else:
            # if the row is a dictionary, map keys to the new column names
            for col in column_names:
                # find the original key that maps to the new snake_case column name
                original_key = next((k for k, v in row.items() if to_snake_case(k) == col), None)
                if original_key:
                    json_row[col] = row[original_key]
                else:
                    json_row[col] = None  # or some default value
        json_data.append(json_row)
    return json_data


def get_non_standard_adm_json(raw_json):
    """
    Function to get non-standard ADM JSON data from raw JSON.
    Returns classified data structured by node name and nested by table name.
    """
    output_json = get_raw_non_standard_adm_json(raw_json)
    standardized_data = convert_keys_and_columns(output_json)

    classified_data = {}
    for unique_table_name, value in standardized_data.items():
        original_table_name = value.get("original_table_name", unique_table_name)
        parent_table_name = value.get("parent_table_name", "")
        node_name = get_node_name_from_llm(original_table_name, parent_table_name)
        json_data = convert_table_to_json(value["data"], value["column_names"])

        if node_name not in classified_data:
            classified_data[node_name] = {"tables": {}}

        if "tables" not in classified_data[node_name]:
            classified_data[node_name]["tables"] = {}

        # Use the unique_table_name to store the data, preventing merges
        classified_data[node_name]["tables"][unique_table_name] = json_data

    return classified_data
