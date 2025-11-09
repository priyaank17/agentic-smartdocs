"""
This module is used to extract metadata from JSON input."""

from datetime import datetime
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage
from src.utils.llm_models.get_llm import get_llm_model
from src.utils.log import logger
from src.data_sheets_v2.get_adm_json.get_meta_data.schema import Metadata
from src.data_sheets_v2.get_adm_json.get_meta_data.postprocess import (
    sync_item_number_and_equipment_tag,
)

parser = PydanticOutputParser(pydantic_object=Metadata)


def format_prompt(json_input):
    """
    Format the prompt for the LLM.
    """
    logger.info("INIT: Formatting prompt for LLM")
    format_instructions = parser.get_format_instructions()
    prompt = (
        "You are a data extraction agent. Extract the following metadata fields "
        "from the given input JSON:\n\n"
        f"{format_instructions}\n\n"
        "Make sure to extract the fields accurately and focus on the following:"
        "\n- 'equipment_name' should be the name of the equipment, like 'Octene Recycle Cooler'."
        "\n- 'equipment_tag' should be the equipment's unique tag, like 'E-3190'."
        "\n- 'item_number' should be the item number unique tag, like 'E-3190'."
        "\n- 'document_number' should be the document number, like 'BCEP-CE-SE-L000E9152'."
        "\n- 'document_name' should be the document name, "
        "like 'Mechanical Data sheet For Octene Recycle Cooler E-3190',"
        "\n- 'manufacture' should be the manufacturer, like 'Atlas Copco'."
        "\n- 'service_name' should be the service name, like 'Octene Recycle Cooler'."
        "\nIf the field is missing or cannot be found, return 'None'.\n\n"
        "\n Make sure to extract the fields accurately and focus on the following:"
        f"JSON Input:\n{json_input}"
    )
    logger.info("DONE: Formatting Prompt for LLM")
    return HumanMessage(content=prompt)


def extract_metadata(json_input):
    """Extract metadata from JSON input."""
    logger.info("INIT: Extracting metadata from JSON input using LLM")
    llm = get_llm_model(model_name="gpt-4o")
    message = format_prompt(json_input)
    # print(message.content)
    response = llm.invoke([message])
    extracted_metadata = parser.parse(response.content)

    # Dynamically set the 'adm_version' to 'ADM_DATA_SHEET' + today's date
    today_date = datetime.now().strftime("%Y-%m-%d")
    extracted_metadata.adm_version = f"ADM_DATA_SHEET_{today_date}"
    extracted_metadata.adm_type = "DATA_SHEET"
    # extracted_metadata.asset_type = asset_type
    logger.info("DONE: Extracting metadata from JSON input")
    return extracted_metadata


def extract_description_metadata_tables(json_data):
    """Extract description and metadata tables from JSON data."""
    filtered_tables = [
        table
        for table in json_data
        if isinstance(table, dict)
        and table.get("table_name") in ["DESCRIPTION", "META DATA"]
    ]
    return filtered_tables


def get_metadata(json_input):
    """Get metadata from JSON input."""
    logger.info("INIT: Getting metadata from JSON input")
    metadata_input_text = extract_description_metadata_tables(json_input)
    extracted_metadata = extract_metadata(metadata_input_text)
    metadata_dict = extracted_metadata.dict()
    updated_meta_data = sync_item_number_and_equipment_tag(metadata_dict)
    logger.info("DONE: Getting metadata from JSON input")
    return updated_meta_data
