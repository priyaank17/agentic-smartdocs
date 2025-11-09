"""Parse the standard property table and generate a mapping dictionary."""

import re
import pandas as pd
from src.utils.log import logger


def parse_categories(nodes_column, column_name=None):
    """determine the node categories for a standard property."""
    # Normalize separators like "and" and ","
    # print("nodes_column", nodes_column)
    if nodes_column is None or pd.isna(nodes_column):
        return []
    # if column_name not in ["parent_table_name", "possible_table_name"]:
    #     # Convert to lowercase and replace " and " with ","
    #     # nodes_column = nodes_column.lower().replace(" and ", ",")
    #     nodes_column = re.sub(r'\s*and\s*', ',', nodes_column, flags=re.IGNORECASE)
    #     nodes_column = nodes_column.lower()
    # # except column name
    # return [
    #     node.strip() for node in nodes_column.split(",") if node.strip()
    # ] if nodes_column else []

    if column_name not in ["parent_table_name", "possible_table_name"]:
        nodes_column = re.sub(r"\s*and\s*", ",", nodes_column, flags=re.IGNORECASE)
        nodes_column = nodes_column.lower()
        return [node.strip() for node in nodes_column.split(",") if node.strip()]

    return [nodes_column.strip().lower()]

    # return [
    #     cat.strip().title().lower() for cat in nodes_column.split(",") if cat.strip()
    # ]


def _generate_mapping_dict(mapping_df, asset_class):
    """
    Generate a dictionary mapping standard property names (and their alternate names)
    to a list of their node categories, handling duplicates as lists.
    """
    logger.info("INIT: Generating mapping dictionary")
    mapping_dict = {}
    # print("mapping_df", mapping_df)

    for _, row in mapping_df.iterrows():
        node_name = parse_categories(row.get("node_name"))
        node_categories = parse_categories(row.get("node_category"))
        node_subpart_type = parse_categories(row.get("node_subpart_type"))
        parent_table_name = parse_categories(row.get("parent_table_name"), "")
        possible_table_name = parse_categories(row.get("possible_table_name"), "")

        entry = {
            "node_name": node_name,
            "node_category": node_categories,
            "node_subpart_type": node_subpart_type,
            "parent_table_name": parent_table_name,
            "possible_table_name": possible_table_name,
        }
        asset_class_name = row["asset_class"].strip().lower()
        if asset_class != asset_class_name:
            continue

        table_key = row.get("possible_table_name", "").strip().lower().replace(" ", "_")
        parent_key = row.get("parent_table_name", "")
        if parent_key and pd.notna(parent_key):
            parent_key = parent_key.strip().lower().replace(" ", "_")
            key = f"{table_key}_{parent_key}"
        else:
            key = table_key
        existing_entries = mapping_dict.setdefault(key, [])
        if entry not in existing_entries:
            existing_entries.append(entry)
    logger.info("DONE: Generating mapping dictionary")
    return mapping_dict


async def prepare_asset_mapping(asset_class):
    """Load the mapping CSV file."""
    logger.info("INIT: Preparing asset mapping")
    csv_path = f"src/constants/standard_detail/{asset_class}_standard_property.csv"
    if not pd.io.common.file_exists(csv_path):
        asset_class = "heat_exchanger_air_cooled"  # Default to a known asset class
        logger.error(f"CSV file does not exist at {csv_path}")
        csv_path = f"src/constants/standard_detail/{asset_class}_standard_property.csv"
    try:
        mapping_df = pd.read_csv(csv_path)
    except Exception as e:
        logger.error(f"Failed to read CSV at {csv_path}: {e}")
        raise

    mapping_dict = _generate_mapping_dict(mapping_df, asset_class)

    logger.info("DONE: Loading mapping CSV")
    return mapping_dict
