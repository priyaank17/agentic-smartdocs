"""This module contains utility functions for local file operations."""
import json


def save_json_local(output_path, output):
    """Save the output to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)


def load_local_json(file_path):
    """Load the JSON file."""
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)
