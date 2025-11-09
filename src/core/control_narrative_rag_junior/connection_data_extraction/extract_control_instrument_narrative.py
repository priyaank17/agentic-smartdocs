"""Extract narrative data from pdf file."""

import json
from dotenv import load_dotenv
from src.utils.log import logger
from src.control_narrative_rag_junior.connection_data_extraction.narrative_llm import (
    get_prompt,
    control_narrative_llm_extraction,
)
from src.utils.get_equipment_index import save_process_equipment_index
from src.prompts.prompt import CONTROL_NARRATIVE_INSTRUMENT_PROMPT_RAG_JUNIOR_PATH
from src.utils.get_junior_response import (
    get_document_data_from_junior_app_runner,
)
from src.data_sheets.constant import get_asset_names_from_s3

load_dotenv()


def extracted_junior_data_for_a_query(model_name, asset_name, document_id):
    """Extract narrative data using Junior API"""
    logger.info("Init: Extracting narrative data using Junior API")
    # question = f"""Provide all control instrument of the {asset_name}."""
    question = f"""Provide relevant instrument information for {asset_name}.
    The output should contain the instrument tag, description,
    and operation_type. Exclude instruments that interact with SIS or alarms.
    The operation_type should be one of:
    ['TRANSMITTER', 'DIRECT_ACTING', 'REVERSE_ACTING', 'FAIL_OPEN', 'FAIL_CLOSE']."""

    junior_extracted_output = get_document_data_from_junior_app_runner(
        model_name, question, [], document_id
    )
    if junior_extracted_output.status_code == 200:
        try:
            response_content = junior_extracted_output.content.decode("utf-8")
            response_json = json.loads(response_content)
            answer = response_json["output"]["answer"]
            logger.info(f"Done: Extracting narrative data using Junior {answer}")
            return answer
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing response: {e}")
    else:
        logger.error(
            f"Request failed with status code: {junior_extracted_output.status_code}"
        )
    return None


def extracted_structured_data_for_a_query(model_name, junior_paragraph):
    """Extract structured output using LLM models."""
    logger.info(
        "Init: Extracting structured output from junior output using LLM models"
    )
    prompt_template = get_prompt(CONTROL_NARRATIVE_INSTRUMENT_PROMPT_RAG_JUNIOR_PATH)
    llm_extracted_output = control_narrative_llm_extraction(
        model_name, junior_paragraph, prompt_template
    )
    logger.info(
        "Done: Extracting structured output from Junior output using LLM models"
    )
    return llm_extracted_output


def get_extracted_data_for_all_query(document_id, model_name, asset_name_list):
    """Extract Extraction of instrument of all
    the asset in control narrative data.."""
    logger.info(
        "Init: Extracting instrument of all the assets in control narrative data."
    )
    output = []
    # junior_data = []
    for asset in asset_name_list:
        junior_output = extracted_junior_data_for_a_query(
            model_name, asset, document_id
        )
        if junior_output:
            query_extract_data = extracted_structured_data_for_a_query(
                model_name, junior_output
            )
            logger.info(f"Extracted data: {query_extract_data}")
            # junior_data.append(junior_output)
            output.extend(query_extract_data)
    logger.info(
        "Done: Extraction of instrument for of all "
        "the asset in control narrative data."
    )
    # save_json_local(
    #     "data/local/mafpp/control_narrative/20_nov/1.instrument_data_junior.txt",
    #     junior_data,
    # )
    return output


def save_json_local(output_path, output):
    """Save the output to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)


async def get_control_instrument_data(bucket_name, plant_id, document_id, model_name):
    """Get data"""
    logger.info("Init: Extraction of instrument of all the assets in control narrative data.")
    asset_table_list_path = (
        f"{plant_id}/documents/control_narrative/{document_id}/assets_table.csv"
    )
    await save_process_equipment_index(bucket_name, plant_id, asset_table_list_path)
    asset_name_list = await get_asset_names_from_s3(bucket_name, asset_table_list_path)
    print("asset_name_list", asset_name_list)
    # asset_name_list = ["LPG HP Separator"]
    control_instrument_data = get_extracted_data_for_all_query(
        document_id, model_name, asset_name_list
    )
    logger.info(
        "Done: Extraction of instrument of all "
        "the assets in control narrative data."
    )
    return control_instrument_data
