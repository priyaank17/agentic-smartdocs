"""This file would be used to pre-process OCR data"""

from src.utils.log import logger


def group_text_annotations_by_y_coordinate(json_data, threshold):
    """Group text annotations by y coordinate"""
    logger.info("INIT: Grouping text annotations by y coordinate.")
    # threshold = 15
    grouped_descriptions = {}

    ocr_file_name = next(iter(json_data))
    logger.info("file_name : %s", ocr_file_name)
    for annotation in json_data[ocr_file_name]["text_annotations"]:
        y_min = min(vertex["y"] for vertex in annotation["bounding_poly"]["vertices"])
        group_key = round(y_min / threshold) * threshold

        if group_key not in grouped_descriptions:
            grouped_descriptions[group_key] = {
                "sentence_string": [],
                "descriptions": [],
            }

        description_data = {
            "word": annotation["description"],
            "x_coordinates": [
                annotation["bounding_poly"]["vertices"][0]["x"],
                annotation["bounding_poly"]["vertices"][1]["x"],
            ],
            "y_coordinates": [
                annotation["bounding_poly"]["vertices"][0]["y"],
                annotation["bounding_poly"]["vertices"][2]["y"],
            ],
        }

        grouped_descriptions[group_key]["sentence_string"].append(
            annotation["description"]
        )
        grouped_descriptions[group_key]["descriptions"].append(description_data)
    logger.info("Done: grouping text annotations by y coordinate.")
    return grouped_descriptions


def combine_words_having_same_y_coordinate(words, threshold):
    """Combine words having same y coordinate"""
    result = []
    words = sorted(words, key=lambda w: w["x_coordinates"][0])
    x1 = words[0]["x_coordinates"][0]
    x2 = words[0]["x_coordinates"][1]
    y1 = words[0]["y_coordinates"][0]
    y2 = words[0]["y_coordinates"][1]
    sentence = words[0]["word"]
    sentence = sentence.replace(",", "")
    current_group = {
        "word": sentence,
        "x_coordinates": [x1, x2],
        "y_coordinates": [y1, y2],
    }
    for i in range(1, len(words)):
        prev_x = words[i - 1]["x_coordinates"][1]
        current_x = words[i]["x_coordinates"][0]
        words[i]["word"] = words[i]["word"].replace(",", "")
        if current_x - prev_x <= threshold:
            sentence += " " + words[i]["word"]
            x1 = min(x1, words[i]["x_coordinates"][0])
            x2 = max(x2, words[i]["x_coordinates"][1])
            y1 = min(y1, words[i]["y_coordinates"][0])
            y2 = max(y2, words[i]["y_coordinates"][1])
        else:
            current_group["word"] = sentence
            current_group["x_coordinates"] = [x1, x2]
            current_group["y_coordinates"] = [y1, y2]
            result.append(current_group.copy())
            x1 = words[i]["x_coordinates"][0]
            x2 = words[i]["x_coordinates"][1]
            y1 = words[i]["y_coordinates"][0]
            y2 = words[i]["y_coordinates"][1]
            sentence = words[i]["word"]
            current_group = {
                "word": sentence,
                "x_coordinates": [x1, x2],
                "y_coordinates": [y1, y2],
            }
    current_group = {
        "word": sentence,
        "x_coordinates": [x1, x2],
        "y_coordinates": [y1, y2],
    }
    result.append(current_group.copy())
    return result


def sort_and_combine_annotations_by_x_coordinate(json_data, threshold_x, threshold_y):
    """Sort and combine annotations by x coordinate"""
    logger.info(
        "INIT: Grouping annotation by y, sorting and combining annotations by x."
    )
    data = group_text_annotations_by_y_coordinate(json_data, threshold_y)
    # threshold_x = 40
    combined_data = {}
    for section_key, section_data in data.items():
        section_data["descriptions"].sort(key=lambda x: x["x_coordinates"][0])
        combined_words = combine_words_having_same_y_coordinate(
            section_data["descriptions"], threshold_x
        )
        combined_data[section_key] = combined_words
    logger.info(
        "Done Grouping annotation by y coord, sorting and combining annotations by x coord."
    )
    return combined_data


def generate_sorted_x_coordinate_data(json_data, threshold_x, threshold_y):
    """Generate sorted x coordinate data"""
    logger.info(
        "INIT: Generating grouped data having word, x_coordinate and y_coordinate"
    )
    data = sort_and_combine_annotations_by_x_coordinate(
        json_data, threshold_x, threshold_y
    )
    sorted_data = dict(sorted(data.items(), key=lambda item: int(item[0])))
    csv_data = ""
    word_positions_from_ocr = []
    for _, value in sorted_data.items():
        for i in value:
            word = i["word"]
            # x_coordinate = i["x_coordinates"][0]
            # y_coordinate = i["y_coordinates"][0]
            x_coordinate = round((i["x_coordinates"][0] + i["x_coordinates"][1]) / 2)
            y_coordinate = round((i["y_coordinates"][0] + i["y_coordinates"][1]) / 2)
            csv_data += f"{word} ({x_coordinate}, {y_coordinate})\n"
            word_positions_from_ocr.append(
                {
                    "word": word,
                    "x_min": i["x_coordinates"][0],
                    "x_max": i["x_coordinates"][1],
                    "y_min": i["y_coordinates"][0],
                    "y_max": i["y_coordinates"][1],
                }
            )
    logger.info("Done: generating grouped data.")
    return word_positions_from_ocr, csv_data


def is_inside_box(bounding_box, bounding_poly):
    """Check if bounding box is inside bounding poly"""
    x, y = bounding_poly[0]["x"], bounding_poly[0]["y"]
    x1, y1 = bounding_box[0][0], bounding_box[0][1]
    x2, y2 = bounding_box[1][0], bounding_box[1][1]
    x3, y3 = bounding_box[2][0], bounding_box[2][1]
    x4, y4 = bounding_box[3][0], bounding_box[3][1]

    return x1 <= x <= x2 and y1 <= y <= y3 and x3 <= x <= x4 and y2 <= y <= y4


def extract_bounding_box(data, bounding_box):
    """Extract bounding box"""
    modified_data = {}
    # modified_data = []
    for page, annotations in data.items():
        modified_annotations = {"text_annotations": []}
        for annotation in annotations["text_annotations"]:
            bounding_poly = annotation["bounding_poly"]["vertices"]
            if is_inside_box(bounding_box, bounding_poly):
                modified_annotations["text_annotations"].append(annotation)
                # modified_data.append(annotation)

        modified_data[page] = modified_annotations

    return modified_data


def sorted_ocr_data_for_data_sheet_table(json_data, bounding_box):
    """Sort OCR data for data sheet table"""
    logger.info("INIT: Sort OCR data for data sheet data")
    del json_data[next(iter(json_data))]["text_annotations"][0]
    json_data = extract_bounding_box(json_data, bounding_box)
    # threshold_x, threshold_y = 40, 15
    threshold_x, threshold_y = 25, 15
    # threshold_x, threshold_y = 15, 5
    word_positions_from_ocr, csv_data = generate_sorted_x_coordinate_data(
        json_data, threshold_x, threshold_y
    )
    data = {"id": 1, "text": csv_data}
    logger.info("DONE: Sorted OCR data for data sheet data")
    return word_positions_from_ocr, data


def is_float(s):
    """Check if string is float"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_property_names_string(json_data, threshold_x, threshold_y):
    """Get property names string"""
    logger.info("INIT: Generating grouped data")
    data = sort_and_combine_annotations_by_x_coordinate(
        json_data, threshold_x, threshold_y
    )
    sorted_data = dict(sorted(data.items(), key=lambda item: int(item[0])))
    csv_data = ""
    for _, value in sorted_data.items():
        for i in value:
            word = i["word"]
            # csv_data += f"{word}\n"
            if not (word.isdigit() or is_float(word)):
                csv_data += f"{word}\n"
    logger.info("Done: generating grouped data.")
    return csv_data


def sorted_ocr_for_property_name_string(json_data, bounding_box):
    """Sort OCR data for property name string"""
    logger.info("INIT: Sort OCR data for property name string")
    json_data = extract_bounding_box(json_data, bounding_box)
    threshold_x, threshold_y = 25, 15
    csv_data = get_property_names_string(json_data, threshold_x, threshold_y)
    logger.info("DONE: Sorted OCR data for property name string")
    return csv_data
