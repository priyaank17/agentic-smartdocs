"""This module provides a way to access JSON files in a folder."""

import json
import os


class JsonFolder:
    """This class provides a way to access JSON files in a folder."""

    def __init__(self, folder_path):
        """Initialize the JsonFolder object."""
        self.folder_path = folder_path

    def __getitem__(self, file_name):
        """This special method allows the object to be subscriptable."""
        full_path = os.path.join(self.folder_path, f"{file_name}.json")
        try:
            with open(full_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return f"No such file: {file_name}.json"
        except json.JSONDecodeError:
            return "Error decoding JSON from the specified file."

    def list_json_files(self):
        """List all JSON files in the folder."""
        return [f for f in os.listdir(self.folder_path) if f.endswith(".json")]
