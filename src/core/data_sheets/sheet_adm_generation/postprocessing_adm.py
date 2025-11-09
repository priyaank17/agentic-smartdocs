"""This module contains functions for postprocessing the ADM JSON data."""

from fuzzywuzzy import fuzz


def convert_to_numerics(adm_json):
    """Converts a string to a float or numeric."""
    if isinstance(adm_json, dict):
        for key, value in adm_json.items():
            if isinstance(value, str) and value.replace(".", "", 1).isdigit():
                adm_json[key] = float(value) if "." in value else int(value)
            else:
                convert_to_numerics(value)
    elif isinstance(adm_json, list):
        for _, item in enumerate(adm_json):
            convert_to_numerics(item)


def add_bounding_boxes(ocr_data, data_sheet_adm_data, threshold=50):
    """Add bounding box data to json_2"""
    for property_entry in data_sheet_adm_data["properties"]:
        best_match = None
        best_score = 0

        for entry_1 in ocr_data:
            match_score = 0
            if entry_1["data_sheet_section"] == property_entry["data_sheet_section"]:
                if entry_1["word"] and property_entry["property_name"]:
                    match_score = fuzz.ratio(
                        property_entry["property_name"].lower(), entry_1["word"].lower()
                    )
                    if (
                        property_entry["property_name"].lower()
                        in entry_1["word"].lower()
                    ):
                        best_match = entry_1
                        best_score = 100
                        break

                if match_score > best_score and match_score >= threshold:
                    best_match = entry_1
                    best_score = match_score

        if best_match:
            property_entry["property_name_bounding_box"] = {
                "x_min": best_match["x_min"],
                "x_max": best_match["x_max"],
                "y_min": best_match["y_min"],
                "y_max": best_match["y_max"],
            }
            get_property_value_bounding_box(
                ocr_data, property_entry, threshold=threshold
            )
        else:
            property_entry["property_name_bounding_box"] = {
                "x_min": None,
                "x_max": None,
                "y_min": None,
                "y_max": None,
            }
            property_entry["property_value_bounding_box"] = {
                "x_min": None,
                "x_max": None,
                "y_min": None,
                "y_max": None,
            }
    return data_sheet_adm_data


def get_property_value_bounding_box(
    ocr_data, property_entry, threshold, property_value_threshold=150
):
    """Add property value bounding boxes considering fuzzy match,
    proximity, and other tie-breakers."""
    property_value = property_entry["property_value"]
    property_name_y_min = property_entry["property_name_bounding_box"]["y_min"]
    property_name_y_max = property_entry["property_name_bounding_box"]["y_max"]

    y_min = property_name_y_min - property_value_threshold
    y_max = property_name_y_max + property_value_threshold

    best_match = None
    min_gap = 2 * property_value_threshold  # Initialize to a large value
    best_score = 0

    for entry in ocr_data:
        word = entry.get("word")
        if word and property_value:
            # Calculate the vertical distance (y-gap)
            gap = abs(property_name_y_min - entry["y_min"])

            # Fuzzy matching (ignoring case) to check if the word resembles the property value
            word = str(word)
            property_value = str(property_value)
            match_score = fuzz.ratio(property_value.lower(), word.lower())

            if (
                y_min <= entry["y_min"] <= y_max
                and match_score >= best_score
                and match_score >= threshold
            ):
                if match_score == best_score:
                    # Tie-breaking logic based on proximity (min_gap)
                    if gap < min_gap:
                        best_match = entry
                        min_gap = gap
                else:
                    best_match = entry
                    best_score = match_score
                    min_gap = gap

    if best_match:
        property_entry["property_value_bounding_box"] = {
            "x_min": best_match["x_min"],
            "x_max": best_match["x_max"],
            "y_min": best_match["y_min"],
            "y_max": best_match["y_max"],
        }
    else:
        property_entry["property_value_bounding_box"] = {
            "x_min": None,
            "x_max": None,
            "y_min": None,
            "y_max": None,
        }
