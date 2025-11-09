"""This module is used to validate the JSON data against the JSON schema"""

import os
import json
import jsonschema
from jsonschema import validate
from src.utils.log import logger


def setup_config():
    """Setup config file"""
    root_folder_path = os.path.abspath("")
    config_file_path = root_folder_path + "/data/configs/config.json"
    with open(config_file_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    control_loops_output_data_path = os.path.join(
        root_folder_path, config["aggregrated_control_loops_json_path"]
    )
    instruments_output_data_path = os.path.join(
        root_folder_path, config["aggregrated_instrument_json_path"]
    )
    control_loops_validation_schema_path = os.path.join(
        root_folder_path, config["control_loops_validation_schema_path"]
    )
    instruments_validation_schema_path = os.path.join(
        root_folder_path, config["instruments_validation_schema_path"]
    )
    config["CONTROL_LOOPS_OUTPUT_DATA_PATH"] = control_loops_output_data_path
    config["INSTRUMENTS_OUTPUT_DATA_PATH"] = instruments_output_data_path
    config["ROOT_FOLDER_PATH"] = root_folder_path
    config["CONTROL_LOOPS_VALIDATION_SCHEMA_PATH"] = (
        control_loops_validation_schema_path
    )
    config["INSTRUMENTS_VALIDATION_SCHEMA_PATH"] = instruments_validation_schema_path
    return config


def files_path(config, validation_schema_path, output_data_path):
    """Load and return the validation schema and data from the config paths."""
    validation_schema_path = config[validation_schema_path]
    output_data_path = config[output_data_path]
    with open(validation_schema_path, encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
    with open(output_data_path, encoding="utf-8") as data_file:
        json_data = json.load(data_file)
    return schema, json_data


def get_validation(schema, json_data):
    """Validate the data against the schema and log the result."""
    try:
        validate(instance=json_data, schema=schema)
        logger.info("JSON data is valid")
    except jsonschema.exceptions.ValidationError as e:
        logger.info("JSON data is not valid")
        print(e)


def schema_validation():
    """Validate control loops and instruments data against their respective schemas."""
    config = setup_config()
    schema_control_loops, control_loops_data = files_path(
        config, "CONTROL_LOOPS_VALIDATION_SCHEMA_PATH", "CONTROL_LOOPS_OUTPUT_DATA_PATH"
    )
    get_validation(schema_control_loops, control_loops_data)
    schema_instruments, instruments_data = files_path(
        config, "INSTRUMENTS_VALIDATION_SCHEMA_PATH", "INSTRUMENTS_OUTPUT_DATA_PATH"
    )
    get_validation(schema_instruments, instruments_data)


if __name__ == "__main__":
    schema_validation()
