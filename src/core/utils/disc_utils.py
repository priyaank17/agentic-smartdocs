"""This module contains utility functions to get data."""

import json
from json import JSONEncoder
import numpy as np


def read_json(file_path):
    """Read json file."""
    with open(file_path, "r", encoding="utf-8") as fp:
        json_data = json.load(fp)
    return json_data


def read_dict_from_json(file_path):
    """Read json file."""
    with open(file_path, "r", encoding="utf-8") as fp:
        json_data = json.load(fp)
    return json_data


def write_json(file_path, json_data):
    """Write json file."""
    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(json_data, fp, ensure_ascii=False)


class NumpyArrayEncoder(JSONEncoder):
    """ "Convert numpy array to json."""

    def default(self, o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        return JSONEncoder.default(self, o)


def to_json(obj):
    """Convert numpy array to json."""
    return json.dumps(obj, cls=NumpyArrayEncoder)


def remove_nonetype_lines(lines):
    """Remove lines with None type."""
    new_lines = []
    for line in lines:
        if line.get("type") is not None:
            new_lines.append(line)
    return new_lines
