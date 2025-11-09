"""This file contains functions for post-processing hallucinated control loops"""

from src.control_narrative_lambda.constant import control_loop_property_name_list
from src.utils.log import logger


def remove_hallucinated_words(control_loop_key, property_name, paragraph):
    """Remove words from the property of a control loop that are not present in the paragraph."""
    word_list = control_loop_key[property_name]
    missing_words = [word for word in word_list if word not in paragraph]
    if missing_words:
        logger.info(
            f"Property {property_name} value not present in the paragraph : {missing_words}"
        )
    matched_words = [word for word in word_list if word in paragraph]
    return matched_words


def resolve_hallucinated_word_in_json(json_data, csv_data):
    """Resolve hallucinated words in control loop json data"""
    logger.info("INIT : resolve_hallucinated_word_in_json")
    for control_loop_key in json_data:
        narrative_id = int(control_loop_key["narrative_id"].split("_")[1])
        matched_row = csv_data.loc[csv_data["id"] == narrative_id]

        if not matched_row.empty:
            matched_text = matched_row["text"].values[0]
            for property_name in control_loop_property_name_list:
                control_loop_key[property_name] = remove_hallucinated_words(
                    control_loop_key, property_name, matched_text
                )
    logger.info("DONE : resolved hallucinated_word_in_json")
    return json_data
