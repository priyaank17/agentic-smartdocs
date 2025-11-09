"""This module contains functions to post-process HMB data."""

import json
from io import StringIO
import pandas as pd
from src.utils.log import logger
from src.utils.storage_utils import (
    upload_file_to_storage,
    fetch_file_via_adapter,
    list_objects_in_storage
)
from src.utils.s3_download_upload import (
    read_csv_from_storage
)


# pylint: disable=too-many-statements
async def process_hmb_data(  # noqa: C901
        folder_path,
        bucket,
        output_json_path,
        metadata_file):
    """
    Processes HMB data from CSV files in a specified S3 folder and converts them to a JSON format.

    Parameters:
    - folder_path (str): Path to the S3 folder containing CSV files.
    - bucket (str): Name of the S3 bucket.
    - output_json_path (str): Path for the output JSON file.
    - metadata_file (str): Path to the metadata JSON file.
    """
    response = await fetch_file_via_adapter(bucket, metadata_file)
    meta_data = response["meta_data"]

    # Function to process each CSV file and convert to JSON
    def process_csv(csv_data, state):
        # Read the CSV data into a DataFrame
        df = pd.read_csv(StringIO(csv_data))

        # Initialize the JSON structure
        json_data = {"meta_data": meta_data, "streams": []}

        # Extract stream numbers from the column names, starting from the third column
        stream_numbers = df.columns[2:]

        # Iterate over each stream number
        for stream_number in stream_numbers:
            state_conditions = {}

            # Iterate over each row to get the properties for this stream number
            for _, row in df.iterrows():
                property_name = row[0]
                value = row[stream_number]
                if pd.isna(property_name) or property_name == "":
                    continue

                if state not in state_conditions:
                    state_conditions[state] = {"state": state, "properties": []}

                state_conditions[state]["properties"].append(
                    {"name": property_name, "value": value}
                )

            # Check if the stream number already exists in json_data["streams"]
            stream_found = False
            for stream in json_data["streams"]:
                if stream["stream_number"] == stream_number:
                    for state_condition in state_conditions.values():
                        stream["operating_conditions"].append(state_condition)
                    stream_found = True
                    break

            if not stream_found:
                json_data["streams"].append(
                    {
                        "stream_number": stream_number,
                        "operating_conditions": list(state_conditions.values()),
                    }
                )

        return json_data

    response = await list_objects_in_storage(bucket, folder_path)

    # Process CSV files
    all_json_data = []
    for obj in response.get("Contents", []):
        if obj["Key"].endswith(".csv"):
            # Load CSV data from S3
            response = await read_csv_from_storage(bucket, obj["Key"])
            csv_data = response["Body"].read().decode("utf-8")

            # Extract the state from the file name
            file_name = obj["Key"].split("/")[-1].replace(".csv", "")
            state = "_".join(file_name.split("_")[2:])

            json_data = process_csv(csv_data, state)
            all_json_data.append(json_data)

    # Combine all JSON data into a single dictionary
    combined_json_data = {"meta_data": meta_data, "streams": []}

    def process_combined_stream(stream, combined_json_data):
        """Process the combined JSON data."""
        stream_found = False
        for combined_stream in combined_json_data["streams"]:
            if combined_stream["stream_number"] == stream["stream_number"]:
                for condition in stream["operating_conditions"]:
                    state_found = False
                    for combined_condition in combined_stream["operating_conditions"]:
                        if combined_condition["state"] == condition["state"]:
                            combined_condition["properties"].extend(condition["properties"])
                            state_found = True
                            break
                    if not state_found:
                        combined_stream["operating_conditions"].append(condition)
                stream_found = True
                break
        return stream_found

    for json_data in all_json_data:
        for stream in json_data["streams"]:
            stream_found = process_combined_stream(stream, combined_json_data)
            if not stream_found:
                combined_json_data["streams"].append(stream)

    await upload_file_to_storage(
        bucket,
        output_json_path,
        json.dumps(combined_json_data)
    )

    logger.info(f"JSON data has been saved to {output_json_path}")
