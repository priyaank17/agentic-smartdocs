"""This file contains Manages file I/O operations,
including saving data locally or uploading it to cloud storage"""

import json
import pandas as pd
from src.utils.s3_download_upload import save_json_to_storage, upload_csv_data
from src.utils.log import logger


def _json_to_csv(json_data):
    """
    Converts a JSON object with tabular data to a CSV file via a DataFrame.
    """
    column_names = json_data["column_names"]
    data = json_data["data"]
    df = pd.DataFrame(data, columns=column_names)
    return df


async def save_data(save_local, table_name, path, post_process_data_json, s3_bucket):
    """Save data to local or s3."""
    df = _json_to_csv(post_process_data_json)
    if save_local:
        table_local_csv_path = f"{table_name}.csv"
        table_local_json_path = f"{table_name}.json"
        df.to_csv(table_local_csv_path, index=False, encoding="utf-8")

        with open(table_local_json_path, "w", encoding="utf-8") as file:
            json.dump(post_process_data_json, file, indent=4)
        logger.info(
            f"Table data saved to {table_local_csv_path} AND {table_local_json_path}"
        )
    else:
        s3_table_json_path = f"{path}/{table_name}.json"
        s3_table_csv_path = f"{path}/{table_name}.csv"
        await save_json_to_storage(s3_bucket, s3_table_json_path, post_process_data_json)
        await upload_csv_data(df, s3_bucket, s3_table_csv_path)
        logger.info(f"Table data saved to {s3_table_csv_path} AND {s3_table_json_path}")
