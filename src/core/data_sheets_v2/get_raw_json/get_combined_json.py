""""
This module contains functions for combining JSON objects into a single JSON object."""

import json
from src.utils.log import logger
from src.utils.storage_utils import (
    upload_file_to_storage,
    fetch_file_via_adapter,
)
from src.utils.s3_download_upload import file_exists_in_storage, read_csv_from_storage


def _csv_to_json(df, table):
    """
    Converts a DataFrame to a JSON object with the structure:
    {
        "table_name": "...",
        "column_names": [...],
        "data": [...]
    }
    """
    json_data = {
        "table_name": table.get("table_name"),
        "table_id": table.get("id"),
        "appearance_number": table.get("appearance_number"),
        "parent_table_name": table.get("parent_table_name"),
        "page_id": table.get("page_id"),
        "page_number": table.get("page_number"),
        "column_names": list(df.columns),
        "data": df.to_dict(orient="records"),
    }
    return json_data


def _add_appearance_number_to_json(json_data, appearance_number):
    """
    Adds new key-value pairs immediately after the 'table_name' key in the JSON data.
    """
    updated_json = {"table_name": json_data["table_name"]}
    new_data = {"appearance_number": appearance_number}
    updated_json.update(new_data)
    for key in json_data:
        if key != "table_name":
            updated_json[key] = json_data[key]

    return updated_json


def _filter_df(df):
    """
    Filter the DataFrame to remove columns with all NaN values.
    """
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    df = df.fillna("")
    return df


async def extract_raw_data_json(input_data_path, bucket, raw_data_json_path, plant_id, document_id):
    """
    Combines multiple JSON objects into a single JSON object.
    """
    logger.info("INIT: Extracting raw data JSON.")
    combine_json_data = []
    input_data = await fetch_file_via_adapter(bucket, input_data_path)
    path = f"{plant_id}/documents/data_sheet/{document_id}"

    for table in input_data["tables_data"]:
        table_name = table.get("table_name")
        if not table_name:
            continue
        table_name = table.get("table_name").lower().replace(" ", "_")
        appearance_number = table.get("appearance_number")
        if appearance_number is not None and appearance_number > 1:
            saved_table_name = f"{table_name}_{appearance_number}"
        else:
            saved_table_name = table_name

        table_csv_path = f"{path}/{saved_table_name}.csv"
        if not file_exists_in_storage(bucket, table_csv_path):
            logger.error(f"CSV file not found at {table_csv_path}, Skip it.")
            continue
        df = await read_csv_from_storage(bucket, table_csv_path)
        df = _filter_df(df)
        table_json_data = _csv_to_json(df, table)
        table_json_path = f"{path}/{saved_table_name}.json"
        await upload_file_to_storage(
            bucket,
            table_json_path,
            json.dumps(table_json_data)
        )
        updated_table_json_data = _add_appearance_number_to_json(
            table_json_data, appearance_number
        )
        combine_json_data.append(updated_table_json_data)
    logger.info("END: Extracting raw data JSON.")
    await upload_file_to_storage(
        bucket,
        raw_data_json_path,
        json.dumps(combine_json_data)
    )
    logger.info(f"Raw data JSON saved to {raw_data_json_path}")
