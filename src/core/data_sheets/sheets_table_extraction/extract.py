"""This file contains the code for the data sheet table extraction process."""

# pylint: disable=no-name-in-module
import os
import json
import io
import csv
import asyncio

from io import StringIO
import pandas as pd
from langchain_community.callbacks.manager import get_openai_callback
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from src.utils.llm_models.get_llm import get_llm_model
from src.data_sheets.preprocessing.preprocess import (
    pre_process_data_sheet,
    pre_process_ocr_property_name,
    get_table_ocr_coordinates_data,
)
from src.data_sheets.sheets_table_extraction.prompt_info import (
    update_prompt_information,
)
from src.prompts.prompt import (
    DATA_SHEET_NOZZLES_PROMPT_PATH,
    DATA_SHEET_TABLE_FORMAT_1_PROMPT_PATH,
    DATA_SHEET_TABLE_FORMAT_2_PROMPT_PATH,
    DATA_SHEET_TABLE_FORMAT_3_PROMPT_PATH,
)
from src.utils.log import logger
from src.data_sheets.property_name_extraction.get_property_name import (
    extract_property_names,
)

# from src.data_sheets.preprocessing.extract_ocr_data import get_ocr_file
from src.utils.invoke_ocr_lambda import get_ocr_file

# from src.data_sheets.sheet_adm_generation.generate_adm import generate_adm
from src.data_sheets.get_standard_details.get_standard_data_sheet_data import (
    get_table_name,
)
from src.utils.storage_utils import (
    upload_file_to_storage,
    fetch_file_via_adapter
)


load_dotenv()
MODEL_NAME = "gpt-4"
CONFIG = None


def _chunks(data, n):
    """Yield successive n-sized chunks from data."""
    for i in range(0, len(data), n):
        yield data[i : i + n]


def _setup_config():
    """Setup config."""
    root_folder_path = os.path.abspath("")
    config_file_path = root_folder_path + "/data/configs/config.json"
    with open(config_file_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)  # pylint: disable=redefined-outer-name
    data_sheets_local_responses_folder_path = os.path.join(
        root_folder_path, config["data_sheets_prompt_responses_folder_path"]
    )
    if not os.path.exists(data_sheets_local_responses_folder_path):
        os.makedirs(data_sheets_local_responses_folder_path)
    # config["ROOT_FOLDER_PATH"] = root_folder_path
    config["DATA_SHEETS_LOCAL_RESPONSES_FOLDER_PATH"] = (
        data_sheets_local_responses_folder_path
    )
    return config


def _get_prompt_template_name_and_response(
    prompt_text, llm, data_sheet_text, columns_name_list, properties_name_list
):
    """Get prompt template name and response from OpenAI API."""
    prompt_template_name = PromptTemplate(
        input_variables=[
            "data_sheet_text_string",
            "columns_name_list",
            "properties_name_list",
        ],
        template=prompt_text,
    )
    name_chain = LLMChain(llm=llm, prompt=prompt_template_name)
    inputs = {
        "data_sheet_text_string": data_sheet_text,
        "columns_name_list": columns_name_list,
        "properties_name_list": properties_name_list,
    }
    with get_openai_callback() as cb_response:
        response = name_chain(inputs=inputs)
    return prompt_template_name, cb_response, response


async def _extract_data_sheet_data_by_prompt(
    prompt_config,
    data_sheet_text,
    columns_name_list,
    properties_name_list,
):
    """Extract data from a data sheet using a given prompt."""
    logger.info("INIT: Extract_Data_By_Prompt function initialized")
    prompt_text = prompt_config.get("prompt_text")
    llm = prompt_config.get("llm")
    prompt_token_path = prompt_config.get("prompt_token_path")
    prompt_template_name, cb_response, response = _get_prompt_template_name_and_response(
        prompt_text, llm, data_sheet_text, columns_name_list, properties_name_list
    )
    await update_prompt_information(
        prompt_template_name, cb_response, prompt_token_path
    )
    logger.info("DONE: Extract_Data_By_Prompt function completed")
    result_string = response["text"].replace("```csv", "").replace("```", "")
    logger.info(result_string)
    return result_string


async def _process_data_sheet(
    data_sheet_text,
    columns_name_list,
    properties_name_list,
    prompt_config,
    paragraph_info,
):
    """Process a data sheet paragraph by paragraph."""
    index = paragraph_info["index"]
    number_of_paragraphs = paragraph_info["number_of_paragraphs"]
    logger.info(f"INIT:Processing paragraph ({index + 1}/{number_of_paragraphs})")
    result_object = await _extract_data_sheet_data_by_prompt(
        prompt_config=prompt_config,
        data_sheet_text=data_sheet_text,
        columns_name_list=columns_name_list,
        properties_name_list=properties_name_list,
    )
    logger.info(f"DONE: Processing paragraph ({index + 1}/{number_of_paragraphs})")
    return result_object


def _get_prompt(data_sheet_prompt_path):
    """Read and return the prompt text from a file."""
    with open(data_sheet_prompt_path, "r", encoding="utf-8") as file:
        prompt_text = file.read()
    return prompt_text


def _add_standard_property_names(df, property_name_dictionary):
    """Add standard property names to a DataFrame based on a dictionary."""
    df["standard_property_name"] = df["property_name"]
    df["property_name"] = df["property_name"].map(property_name_dictionary)

    columns = ["standard_property_name"] + [
        col for col in df.columns if col != "standard_property_name"
    ]

    df = df[columns]
    return df


async def extract_data_sheet_data(
    data_sheet_text_list,
    data_sheet_prompt_path,
    columns_name_list,
    property_config,
    prompt_token_path,
):
    """Extract data from a data sheet using a given prompt."""
    logger.info("INIT: Extract  Data Sheet Data function initialized.")
    prompt_text = _get_prompt(data_sheet_prompt_path)
    number_of_paragraphs = len(data_sheet_text_list)
    llm = get_llm_model(model_name=MODEL_NAME)
    results = []
    prompt_config = {
        "prompt_text": prompt_text,
        "llm": llm,
        "prompt_token_path": prompt_token_path,
    }
    property_name_list = property_config["property_name_list"]
    property_name_dictionary = property_config["property_name_dictionary"]

    # Process in smaller chunks
    for data_sheet_chunk in _chunks(list(enumerate(data_sheet_text_list)), 4):
        # Create a list of tasks
        tasks = [
            _process_data_sheet(
                item[1],
                columns_name_list,
                property_name_list,
                prompt_config,
                paragraph_info={
                    "index": item[0],
                    "number_of_paragraphs": number_of_paragraphs,
                },
            )
            for item in data_sheet_chunk
        ]

        # Await all tasks concurrently
        chunk_results = await asyncio.gather(*tasks)
        results.extend(chunk_results)

    csv_content = results[0]
    cleaned_csv_content = _clean_csv_content(csv_content)
    logger.info(f"cleaned_csv_content {cleaned_csv_content}")
    csv_input = io.StringIO(cleaned_csv_content)
    df = pd.read_csv(csv_input)
    if property_name_dictionary:
        df = _add_standard_property_names(df, property_name_dictionary)
    logger.info("DONE: Extract Data Sheet Data function completed")
    return df


def _clean_csv_content(csv_content):
    """Clean CSV content by ensuring each line has the correct number of fields."""
    lines = csv_content.strip().split("\n")
    header = lines[0]
    num_columns = len(list(csv.reader([header]))[0])
    cleaned_lines = [header]

    for line in lines[1:]:
        if line.strip():
            fields = list(csv.reader([line]))[0]
            fields = [field.strip().replace('"', "") for field in fields]
            if len(fields) > num_columns:
                # Combine extra fields into one column
                fields[num_columns - 1 :] = [",".join(fields[num_columns - 1 :])]
            elif len(fields) < num_columns:
                fields += [""] * (num_columns - len(fields))

            cleaned_line = '"' + '","'.join(fields) + '"'
            cleaned_lines.append(cleaned_line)

    cleaned_csv_content = "\n".join(cleaned_lines)
    return cleaned_csv_content


def _get_table(ocr_json_data, bounding_box):
    """Extract the text of a table from OCR JSON data within a given bounding box."""
    ocr_sorted_data = pre_process_data_sheet(ocr_json_data, bounding_box)
    table_text_list = [ocr_sorted_data["text"]]
    return table_text_list


def _get_property_name(
    plant_id, ocr_json_data, bounding_box, table_name, asset_class
):  # pylint: disable=redefined-outer-name
    """Extract the standard property name for a given asset class and table."""
    logger.info(
        f"INIT: Extract standard property name of {asset_class} asset class for {table_name} table"
    )

    sorted_ocr_data = pre_process_ocr_property_name(ocr_json_data, bounding_box)
    property_name_list, property_name_dictionary = extract_property_names(
        plant_id, asset_class, table_name, sorted_ocr_data
    )
    logger.info(
        f"DONE: Extract standard property name of {asset_class} asset_class for {table_name} table"
    )
    return property_name_list, property_name_dictionary


async def _nozzles_table(ocr_json_data, prompt_token_path, table_config):
    """Extract data from a nozzles table."""
    bounding_coordinates = table_config.get("bounding_coordinates")
    asset_class = table_config.get("asset_class")
    columns_name_list = table_config.get("column_names")
    logger.info(f"Extract for NOZZLES table of {asset_class}")
    nozzle_table_text_list = _get_table(ocr_json_data, bounding_coordinates)
    property_name_list = [None]
    property_name_dictionary = {}
    property_config = {
        "property_name_list": property_name_list,
        "property_name_dictionary": property_name_dictionary,
    }
    nozzles_table_df = await extract_data_sheet_data(
        nozzle_table_text_list,
        DATA_SHEET_NOZZLES_PROMPT_PATH,
        columns_name_list,
        property_config,
        prompt_token_path,
    )
    logger.info("DONE: Extracted for NOZZLES table")
    return nozzles_table_df


async def _table_format_1(ocr_json_data, prompt_token_path, table_config):
    """Extract data from a table_format_1, an unstructured table."""
    table_name = table_config.get("table_name")
    bounding_coordinates = table_config.get("bounding_coordinates")
    plant_id = table_config.get("plant_id")
    asset_class = table_config.get("asset_class")
    logger.info(f"Extract for {table_name}")
    table_format_1_text_list = _get_table(ocr_json_data, bounding_coordinates)
    columns_name_list = ["property_name", "value"]
    property_name_list, property_name_dictionary = _get_property_name(
        plant_id, ocr_json_data, bounding_coordinates, table_name, asset_class
    )
    property_config = {
        "property_name_list": property_name_list,
        "property_name_dictionary": property_name_dictionary,
    }
    logger.info(f"Extracted property_name_list {property_name_list}")
    if property_name_list:
        table_format_1_df = await extract_data_sheet_data(
            table_format_1_text_list,
            DATA_SHEET_TABLE_FORMAT_1_PROMPT_PATH,
            columns_name_list,
            property_config,
            prompt_token_path,
        )
        logger.info(f"DONE: Extracted for {table_name}")
        return table_format_1_df

    logger.error(f"No property names found for {table_name}")
    return None


async def _table_format_2(ocr_json_data, prompt_token_path, table_config):
    """Extract data from table_format_2, a structured table."""
    table_name = table_config.get("table_name")
    bounding_coordinates = table_config.get("bounding_coordinates")
    plant_id = table_config.get("plant_id")
    asset_class = table_config.get("asset_class")
    columns_name_list = table_config.get("column_names")
    logger.info(f"Extract for {table_name}")

    table_format_2_text_list = _get_table(ocr_json_data, bounding_coordinates)
    property_name_list, property_name_dictionary = _get_property_name(
        plant_id, ocr_json_data, bounding_coordinates, table_name, asset_class
    )
    property_config = {
        "property_name_list": property_name_list,
        "property_name_dictionary": property_name_dictionary,
    }
    logger.info(f"Extracted property_name_list {property_name_list}")
    if property_name_list:
        table_format_2_df = await extract_data_sheet_data(
            table_format_2_text_list,
            DATA_SHEET_TABLE_FORMAT_2_PROMPT_PATH,
            columns_name_list,
            property_config,
            prompt_token_path,
        )
        logger.info(f"DONE: Extracted for {table_name}")
        return table_format_2_df
    logger.error(f"No property names found for {table_name}")
    return None


async def _table_format_3(ocr_json_data, prompt_token_path, table_config):
    """Extract data from table_format_3, a table with oly column names"""
    table_name = table_config.get("table_name")
    bounding_coordinates = table_config.get("bounding_coordinates")
    columns_name_list = table_config.get("column_names")
    logger.info(f"Extract for {table_name}")

    table_format_3_text_list = _get_table(ocr_json_data, bounding_coordinates)
    property_config = {
        "property_name_list": [None],
        "property_name_dictionary": {},
    }
    table_format_3_df = await extract_data_sheet_data(
        table_format_3_text_list,
        DATA_SHEET_TABLE_FORMAT_3_PROMPT_PATH,
        columns_name_list,
        property_config,
        prompt_token_path,
    )
    logger.info(f"DONE: Extracted for {table_name}")
    return table_format_3_df


async def _ocr_data(bucket, image_path, ocr_output_json_path):
    """Get OCR output from a file in a bucket."""
    ocr_output = await get_ocr_file(bucket, image_path, ocr_output_json_path)
    return ocr_output


async def _process_image_to_table_data(
    ocr_json_data,
    prompt_token_path,
    table_config,
):
    """Process image data into a table."""

    if not ocr_json_data:
        return None
    table_name = table_config.get("table_name")
    column_names = table_config.get("column_names")
    if table_name == "nozzle":
        nozzle_columns_to_insert = ["nozzle_number", "subpart_name", "connection_type"]
        for i, column in enumerate(nozzle_columns_to_insert):
            if column not in column_names:
                column_names.insert(i, column)
        return await _nozzles_table(ocr_json_data, prompt_token_path, table_config)

    if column_names:
        standard_table_list = get_table_name()
        if table_name in standard_table_list:
            if not any(name.startswith("property") for name in column_names):
                column_names.insert(0, "property_name")
            return await _table_format_2(ocr_json_data, prompt_token_path, table_config)
        return await _table_format_3(ocr_json_data, prompt_token_path, table_config)
    return await _table_format_1(ocr_json_data, prompt_token_path, table_config)


def _save_table_local(table_name, df, config):
    """Save a DataFrame as a CSV file locally."""
    filename = f"/{table_name}.csv"
    output_filepath = config["DATA_SHEETS_LOCAL_RESPONSES_FOLDER_PATH"] + filename
    df.to_csv(output_filepath, index=False, encoding="utf-8")
    logger.info(f"The result object is written to {output_filepath}")


def _update_description_table(df, asset_tag_number, asset_name, asset_class):
    """Update the description table with asset information."""

    def update_or_add_row(df, property_name, value):
        if property_name in df["standard_property_name"].values:
            df.loc[df["standard_property_name"] == property_name, "value"] = (
                value.upper()
            )
        else:
            new_row = pd.DataFrame(
                [[property_name, property_name, value.upper()]], columns=df.columns
            )
            df = pd.concat([df, new_row], ignore_index=True)
        return df

    df = update_or_add_row(df, "equipment_tag", f"{asset_tag_number}")
    df = update_or_add_row(df, "equipment_name", asset_name)
    df = update_or_add_row(df, "equipment_class", asset_class)
    return df


async def get_data(input_data_path, bucket, local_path=False):
    """Get data from a JSON file in a bucket and process it."""
    input_data = await fetch_file_via_adapter(bucket, input_data_path)
    ocr_highlight_bounding_box = []
    document_id = input_data["meta_data"].get("document_id")
    asset_tag_number = input_data["meta_data"].get("asset_tag")
    asset_class = input_data["meta_data"].get("asset_class").lower().replace(" ", "_")
    asset_name = input_data["meta_data"].get("asset_name")
    plant_id = input_data["meta_data"].get("plant_id")
    path = f"{plant_id}/documents/data_sheet/{document_id}"
    prompt_token_path = f"{plant_id}/documents/data_sheet"
    for table in input_data["tables_data"]:
        page_id = table.get("page_id")
        table_name = table.get("table_name")
        if not table_name:
            continue
        table_name = table.get("table_name").lower()
        appearance_number = table.get("appearance_number")
        # Combined these two variables into a base path calculation
        image_path = f"{path}/{page_id}"
        bounding_box = table.get("table_bounding_box")
        bounding_coordinates = [
            (round(float(bounding_box["x_min"])), round(float(bounding_box["y_min"]))),
            (round(float(bounding_box["x_max"])), round(float(bounding_box["y_min"]))),
            (round(float(bounding_box["x_min"])), round(float(bounding_box["y_max"]))),
            (round(float(bounding_box["x_max"])), round(float(bounding_box["y_max"]))),
        ]
        column_names = [
            col.get("name", "").lower().replace(" ", "_")
            for col in table.get("columns", [])
        ]

        table_config = {
            "table_name": table_name,
            "bounding_coordinates": bounding_coordinates,
            "plant_id": plant_id,
            "asset_class": asset_class,
            "column_names": column_names,
        }
        # Use the base path to derive both paths
        ocr_json_data = await _ocr_data(bucket, image_path, f"{image_path}.json")
        ocr_highlight_bounding_box = (
            ocr_highlight_bounding_box
            + get_table_ocr_coordinates_data(ocr_json_data, table_config)
        )
        df = await _process_image_to_table_data(
            ocr_json_data,
            prompt_token_path,
            table_config,
        )
        if table_name == "description":
            df = _update_description_table(df, asset_tag_number, asset_name, asset_class)
        if appearance_number is not None and appearance_number > 1:
            table_name = f"{table_name}_{appearance_number}"
        if df is not None and not df.empty:
            csv_buffer = StringIO()
            df.to_csv(csv_buffer)
            await upload_file_to_storage(
                bucket,
                f"{path}/{table_name}.csv",
                csv_buffer.getvalue(),
            )
            logger.info(f"saved {table_name} table as {path}/{table_name}.csv")
            if local_path:
                # pylint: disable=redefined-outer-name, invalid-name
                CONFIG = _setup_config()
                _save_table_local(table_name, df, CONFIG)
    logger.info("INIT: generate base adm json file")
    await upload_file_to_storage(
        bucket,
        f"{path}/ocr_bounding_box.json",
        ocr_highlight_bounding_box,
    )
    # generate_adm(input_data_path, path)
    # logger.info("Done: generated base adm json file")
