"""This module contains utility functions for postprocessing the received assets."""

import os
from src.utils.log import logger
from src.utils.s3_download_upload import read_csv_from_storage

ROOT_FOLDER_PATH = os.path.abspath("")


def get_asset_name_from_id(connection, bucket_name, expected_asset_csv):
    """Get asset name from asset id."""
    logger.info("INIT: get_asset_name_from_id")
    df = read_csv_from_storage(bucket=bucket_name, path=expected_asset_csv)
    asset_id = connection["asset_id"]
    logger.info(f"asset_id: {asset_id}")
    try:
        asset_id = int(asset_id.split("_")[1])
        logger.info(f"asset_id: {asset_id}")
        row = df[df["id"] == asset_id]
        logger.info(f"row: {row}")
        asset_name = row.iloc[0]["asset_name"]
        logger.info(f"asset_name: {asset_name}")
        return asset_name
    except IndexError:
        logger.error("Invalid asset_id format.")
        return None


def read_asset_names_from_csv(bucket_name, expected_asset_csv, column_name):
    """Read asset names from csv."""
    logger.info("INIT: read_asset_names_from_csv")
    df = read_csv_from_storage(bucket=bucket_name, path=expected_asset_csv)
    asset_names_list = df[column_name].tolist()
    logger.info("DONE: the asset_names list is created")
    return asset_names_list
