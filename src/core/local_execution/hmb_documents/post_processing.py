"""This module contains functions to post process HMB documents"""
# pylint: disable=invalid-name
import json
import os


def setup_config():
    """This function sets up the config"""
    ROOT_FOLDER_PATH = os.path.abspath("")
    CONFIG_FILE_PATH = os.path.join(ROOT_FOLDER_PATH, "data/configs/config.json")
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    HMB_OUTPUT_DATA_PATH = os.path.join(ROOT_FOLDER_PATH, config["hmb_output_data_path"])

    config["ROOT_FOLDER_PATH"] = ROOT_FOLDER_PATH
    config["HMB_OUTPUT_DATA_PATH"] = HMB_OUTPUT_DATA_PATH
    return config


def transform_data(data):
    """This function transforms the data"""
    transformed_data = []
    for item in data:
        if item.get("name") and item.get("value"):
            names = item["name"].split("\n")
            values = item["value"].split("\n")
            for name, value in zip(names, values):
                transformed_data.append({
                    "stream_number": item["stream_number"],
                    "name": name,
                    "value": value
                })
    return transformed_data


def reformat_streams(transformed_data):
    """This function reformats the streams"""
    stream_objects = {}
    for stream_data in transformed_data:
        stream_number = stream_data["stream_number"]
        if stream_number not in stream_objects:
            stream_objects[stream_number] = {"stream_number": stream_number}
        stream_objects[stream_number][stream_data["name"]] = stream_data["value"]
    return list(stream_objects.values())


def rename_keys(stream_objects):
    """This function renames the keys"""
    key_mapping = {
        "stream_number": "stream_number",
        "Phase": "phase",
        "Molar - Vap. Frac.": "molar_vapor_fraction",
        "Temperature [F]": "temperature",
        "Pressure [psig]": "pressure",
        "Vapor [MMSCFD]": "vapor",
        "Molecular Weight": "molecular_weight",
        "Hydrocarbon Actual BPD": "hydrocarbon_actual_bpd",
        "Water Actual BPD": "water_actual_bpd",
        "Heat Flow [MMBtu/hr]": "heat_flow",
        "H2O": "h20",
        "H2S": "h2s",
        "CO2": "co2",
        "Nitrogen": "nitrogen",
        "Methane": "methane",
        "Ethane": "ethane",
        "Propane": "propane",
        "i-Butane": "i_butane",
        "n-Butane": "n_butane",
        "i-Pentane": "i_pentane",
        "n-Pentane": "n_pentane",
        "n-Hexane": "n_hexane",
        "n-Heptane": "n_heptane",
        "n-Octane": "n_octane",
        "n-Nonane": "n_nonane",
        "nC10+": "n_c10_plus",
        "Total (lbmole/hr)": "total"
    }
    for stream in stream_objects:
        for old_key, new_key in key_mapping.items():
            if old_key in stream:
                stream[new_key] = stream.pop(old_key)
    return stream_objects


def post_processing_hmb_data(input_file_path):
    """This function post processes HMB data"""
    print(input_file_path)
    config = setup_config()
    output_file_path = config["HMB_OUTPUT_DATA_PATH"]
    with open(input_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    transformed_data = transform_data(data)
    stream_objects = reformat_streams(transformed_data)
    renamed_streams = rename_keys(stream_objects)

    with open(output_file_path, "w", encoding="utf-8") as file:
        print(f"Saving renamed streams to {output_file_path}")
        json.dump(renamed_streams, file, indent=4)
