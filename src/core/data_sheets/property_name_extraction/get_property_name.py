"""This module contains functions for retrieving and processing property names."""

import json
import re
from fuzzywuzzy import fuzz
import pandas as pd
from src.data_sheets.property_name_extraction.property_name_llm import (
    retrieve_property_names_using_llm,
)
from src.prompts.prompt import PROPERTY_NAME_PROMPT_PATH
from src.utils.log import logger
from src.data_sheets.constant import (
    get_standard_property_df,
    get_specific_standard_df,
    standard_property_name_list_path,
    split_alternate_names
)


def find_matching_every_properties_in_paragraph(properties, paragraph, threshold=40):
    """Find matching properties in a paragraph."""
    logger.info("INIT: find_matching_properties_in_paragraph called")
    paragraph_lower = paragraph.lower()
    words = paragraph_lower.split()
    presence_dict = {}
    presence_list = []

    for prop in properties:
        prop_lower = prop.lower()
        matched_word = None
        matched_accuracy = 0
        for word in words:
            if fuzz.ratio(prop_lower, word) >= threshold:
                if fuzz.ratio(prop_lower, word) > matched_accuracy:
                    matched_word = word
                    matched_accuracy = fuzz.ratio(prop_lower, word)
        presence_dict[prop] = matched_word
        if matched_word is not None:
            presence_list.append(prop)
    logger.info("DONE: find_matching_properties_in_paragraph executed")
    return presence_list


def combine_standard_property_names(df, columns):
    """Combine standard property names from a DataFrame."""
    melted_df = df.melt(value_vars=columns, value_name="property_name")
    melted_df = melted_df.dropna(subset=["property_name"])
    melted_df = melted_df[melted_df["property_name"] != ""]
    return melted_df["property_name"].unique().tolist()


def match_properties_of_that_row(paragraph, row_properties, threshold=45):
    """Match properties of that row in a paragraph."""
    paragraph_lower = paragraph.lower()
    words = paragraph_lower.split()
    matched_word = None
    matched_accuracy = 0
    for prop in row_properties:
        prop_lower = prop.lower()
        for word in words:
            ratio = fuzz.ratio(prop_lower, word.lower())
            if ratio >= threshold and ratio > matched_accuracy:
                matched_word = prop
                matched_accuracy = ratio
    return matched_word


def select_best_match(
    columns_to_extract,
    standard_property_df,
    paragraph,
    match_in_paragraph,
    match_one_property_in_row,
):
    """Select the best match for a property name in a paragraph."""
    if not match_in_paragraph:
        final_property_list = combine_standard_property_names(
            standard_property_df, columns_to_extract
        )
    else:
        if not match_one_property_in_row:
            properties_list = combine_standard_property_names(
                standard_property_df, columns_to_extract
            )
            final_property_list = find_matching_every_properties_in_paragraph(
                properties_list, paragraph
            )
        else:
            filtered_properties = {}
            for _, row in standard_property_df.iterrows():
                row_properties = [
                    row[col] for col in columns_to_extract if pd.notna(row[col])
                ]
                best_match = match_properties_of_that_row(paragraph, row_properties)
                if best_match:
                    filtered_properties[row["standard_property_name"]] = best_match
            final_property_list = list(filtered_properties.values())
    return final_property_list


def load_best_match_standard_property_name(
    asset_class,
    table_name,
    paragraph,
    match_in_paragraph,
    match_one_property_in_row,
):
    """Load best matched standard property name from
    company specific standard property according to asset_class
      and table name."""
    logger.info(
        f"""INIT: Load best matched standard property name from
        company specific standard property according to asset_class
        and table name {asset_class}, {table_name}"""
    )
    property_name_df = get_standard_property_df(standard_property_name_list_path)
    property_name_df = get_specific_standard_df(property_name_df, asset_class)
    possible_table_columns = [
        col for col in property_name_df.columns if col.startswith("possible_table_")
    ]
    filtered_df = property_name_df[
        property_name_df[possible_table_columns].eq(table_name).any(axis=1)
    ]
    filtered_df = split_alternate_names(filtered_df)
    columns_to_extract = [
        column
        for column in filtered_df.columns
        if column.startswith("alternate_name") or column == "standard_property_name"
    ]
    # standard_property_names = combine_standard_property_names(
    #     filtered_df, columns_to_extract
    # )
    property_names_list = select_best_match(
        columns_to_extract,
        filtered_df,
        paragraph,
        match_in_paragraph,
        match_one_property_in_row,
    )
    logger.info(
        f"""DONE: Loaded best matched standard property name
        from company specific standard property, {property_names_list}"""
    )
    return property_names_list


def save_properties_to_csv(properties, filename):
    """Save a list of properties to a CSV file with a single column named 'property_name'."""
    df = pd.DataFrame(properties, columns=["property_name"])
    df.to_csv(filename, index=False)
    logger.info(f"Data has been written to {filename}")


def extract_expected_output(output_str):
    """Extract substrings enclosed in double quotes from a string."""
    if not isinstance(output_str, str):
        output_str = str(output_str)

    return re.findall(r'"(.*?)"', output_str)


def extract_expected_dictionary_output(data):
    """Parse a JSON string and return the resulting dictionary."""
    if isinstance(data, list):
        json_str = "".join(data)
    else:
        json_str = data
    try:
        json_str = json_str.strip('"')
        dictionaries = json.loads(json_str)
    except json.JSONDecodeError:
        logger.error("Error: Invalid JSON format.")
        return None

    return dictionaries


def retrieve_property_name_dictionary_using_llm(
    plant_id, paragraph, property_name_prompt_path, property_name_list
):
    """Retrieve property name dictionary using LLM."""
    property_name_output = retrieve_property_names_using_llm(
        plant_id, paragraph, property_name_prompt_path, property_name_list
    )
    property_name_dictionary = extract_expected_dictionary_output(property_name_output)
    return property_name_dictionary


def extract_property_names(
    plant_id,
    asset_class,
    table_name,
    paragraph,
    **kwargs,
):
    """Extract property names."""
    logger.info("INIT: extract_property_names function called")
    match_in_paragraph = kwargs.get("match_in_paragraph", False)
    retrieve_using_llm = kwargs.get("retrieve_using_llm", True)
    match_one_property_in_row = kwargs.get("match_one_property_in_row", False)
    property_name_list = load_best_match_standard_property_name(
        asset_class,
        table_name,
        paragraph,
        match_in_paragraph,
        match_one_property_in_row,
    )
    # save_properties_to_csv(
    #     property_name_list, f"data/data_sheet/sanha/step1_output/hbg_5765/{table_name}.csv"
    # )
    property_name_dictionary = {}
    if property_name_list and retrieve_using_llm:
        property_name_dictionary = retrieve_property_name_dictionary_using_llm(
            plant_id, paragraph, PROPERTY_NAME_PROMPT_PATH, property_name_list
        )
        logger.info(f"property name prompt output: {property_name_dictionary}")
        if not property_name_dictionary:
            logger.error("No property name dictionary found")
            return [], {}
        property_name_dictionary = interchange_keys_values(property_name_dictionary)
        property_name_list = list(property_name_dictionary.keys())
        logger.info("DONE: executed extract_property_names function")
        # step_check_file_name = f"data/hbg_5765/{table_name}.csv"
        # save_properties_to_csv(
        #     list(property_name_dictionary.keys()), step_check_file_name
        # )
        return property_name_list, property_name_dictionary
    logger.error("No property names found")
    return [], {}


def interchange_keys_values(original_dict):
    """Interchange the keys and values of the given dictionary."""
    interchanged_dict = {}

    for key, value in original_dict.items():
        if isinstance(value, list):
            for v in value:
                interchanged_dict[v] = key
        else:
            interchanged_dict[value] = key

    return interchanged_dict
