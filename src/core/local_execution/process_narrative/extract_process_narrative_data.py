"""This module consists of functions to extract data sheet data in Local"""

import os
import json
import boto3
from src.process_narrative.extract_data import extract_data
from src.utils.s3_download_upload import read_csv_from_storage
from src.utils.log import logger

ROOT_FOLDER_PATH = os.path.abspath("")
CONFIG_FILE_PATH = ROOT_FOLDER_PATH + "/data/configs/config.json"
s3 = boto3.client("s3")


def load_config_and_necessary_variables():
    """Load config file and necessary variables for data sheet accuracy."""
    logger.info("INIT: load_config_and_necessary_variables")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    process_narrative_path = os.path.join(
        ROOT_FOLDER_PATH, config["control_narrative_path"]
    )
    config["PROCESS_NARRATIVE_PATH"] = process_narrative_path
    config["PLANT_ID"] = config["plant_id"]
    config["DOCUMENT_ID"] = config["document_id"]
    config["BUCKET_NAME"] = config["bucket_name"]
    return config


if __name__ == "__main__":
    CONFIG = load_config_and_necessary_variables()
    PLANT_ID = CONFIG["PLANT_ID"]
    DOCUMENT_ID = CONFIG["DOCUMENT_ID"]
    BUCKET_NAME = CONFIG["BUCKET_NAME"]
    # PLANT_ID = "cd0a68f4-664f-4e83-937e-06ff06e8ce49"
    # DOCUMENT_ID = "2dbf6b68-ac72-4d45-8839-a4451885ce9f"
    # BUCKET_NAME = "artisanbucketoregon18510-qatide"

    logger.info("INIT: Extracting Process Narrative Data")
    logger.info("Reading Asset JSON from s3")
    asset_csv_path = (
        "public/"
        + PLANT_ID
        + "/DOCS/PROCESS_NARRATIVE/"
        + DOCUMENT_ID
        + "/assets_table.csv"
    )

    logger.info("Reading Asset CSV from s3")
    narrative_csv_path = (
        "public/"
        + PLANT_ID
        + "/DOCS/PROCESS_NARRATIVE/"
        + DOCUMENT_ID
        + "/narrative_paragraphs.csv"
    )
    input_bounding_box_config_path = (
        "public/"
        + PLANT_ID
        + "/DOCS/PROCESS_NARRATIVE/"
        + DOCUMENT_ID
        + "/input_data.json"
    )
    narrative_text = read_csv_from_storage(bucket=BUCKET_NAME, path=narrative_csv_path)
    pnid_connections_json_path = (
        "public/"
        + PLANT_ID
        + "/DOCS/PROCESS_NARRATIVE/"
        + DOCUMENT_ID
        + "/p&id_source_destination_connection.json"
    )
    s3_response = s3.get_object(Bucket=BUCKET_NAME, Key=pnid_connections_json_path)
    pid_source_destination_connection_data = json.loads(
        s3_response["Body"].read().decode("utf-8")
    )
    extracted_json_s3_file_key = (
        "public/"
        + PLANT_ID
        + "/DOCS/PROCESS_NARRATIVE/"
        + DOCUMENT_ID
        + "/extracted_data.json"
    )
    connections_json_file_key = (
        "public/"
        + PLANT_ID
        + "/DOCS/PROCESS_NARRATIVE/"
        + DOCUMENT_ID
        + "/connections.json"
    )
    MODEL_NAME = "gpt-4"
    asset_text = read_csv_from_storage(bucket=BUCKET_NAME, path=asset_csv_path)
    post_process_connection_path = (
        "public/"
        + PLANT_ID
        + "/DOCS/PROCESS_NARRATIVE/"
        + DOCUMENT_ID
        + "/"
        + DOCUMENT_ID
        + ".PROCESS_NARRATIVE.adm.json"
    )
    extracted_json_file_key = extracted_json_s3_file_key
    process_narrative_args = (
        narrative_text,
        asset_text,
        BUCKET_NAME,
        pnid_connections_json_path,
        extracted_json_file_key,
        connections_json_file_key,
        MODEL_NAME,
        pid_source_destination_connection_data,
        post_process_connection_path,
        input_bounding_box_config_path,
    )
    extract_data(
        process_narrative_args,
    )
    logger.info("Process Narrative Data extracted successfully")
