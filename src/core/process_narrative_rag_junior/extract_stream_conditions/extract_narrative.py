"""Extract narrative data from pdf file."""

import json
from dotenv import load_dotenv
from src.utils.log import logger
from src.process_narrative_rag_junior.extract_stream_conditions.narrative_llm import (
    get_prompt,
    llm_extraction,
    llm_wrapper,
)
from src.utils.storage_utils import (
    upload_file_to_storage
)
from src.utils.get_equipment_index import save_process_equipment_index
from src.process_narrative_rag_junior.extract_stream_conditions import (
    generate_process_narrative_stream_adm,
)
from src.process_narrative_rag_junior.get_junior_response import (
    load_junior_input,
)
from src.utils.get_junior_response import (
    get_document_data_from_junior_app_runner,
)
from src.prompts.prompt import (
    PROCESS_NARRATIVE_STREAM_CONDITIONS_WRAPPER_PROMPT_JUNIOR_PATH,
    PROCESS_NARRATIVE_STREAM_CONDITIONS_PARAGRAPH_PROMPT_PATH,
)
from src.data_sheets.constant import get_asset_names_from_s3
from src.prompts.junior_input_prompt import (
    PROCESS_NARRATIVE_STREAM_CONDITIONS_JUNIOR_INPUT_PATH,
)

# from src.utils.local_utils import save_json_local

get_process_narrative_adm = (
    generate_process_narrative_stream_adm.get_process_narrative_adm
)

load_dotenv()


def _extracted_junior_data_for_a_query(model_name, equipment_name, document_id):
    """Extract narrative data using Junior API"""
    logger.info("Init: Extracting narrative data using Junior API")
    junior_input_path = PROCESS_NARRATIVE_STREAM_CONDITIONS_JUNIOR_INPUT_PATH
    junior_input = load_junior_input(junior_input_path, equipment_name=equipment_name)
    junior_extracted_output = get_document_data_from_junior_app_runner(
        model_name, junior_input, [], document_id
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


def _extract_stream_conditions(
    model_name, equipment_name, equipment_section_junior_output
):
    """Extract stream conditions from process narrative data using LLM"""
    logger.info("Init: Extracting stream conditions from process narrative data.")
    prompt_template = get_prompt(
        PROCESS_NARRATIVE_STREAM_CONDITIONS_PARAGRAPH_PROMPT_PATH
    )
    llm_query = f"equipment_name: {equipment_name}"
    llm_extracted_stream_conditions_output = llm_extraction(
        model_name, equipment_section_junior_output, llm_query, prompt_template
    )
    return llm_extracted_stream_conditions_output


def extracted_structured_data_wrapper(
    model_name, llm_extracted_stream_conditions_output
):
    """Extract structured output using LLM models."""
    logger.info(
        "Init: Extracting structured output from junior output using LLM models"
    )
    prompt_template = get_prompt(
        PROCESS_NARRATIVE_STREAM_CONDITIONS_WRAPPER_PROMPT_JUNIOR_PATH
    )

    llm_extracted_output = llm_wrapper(
        model_name, llm_extracted_stream_conditions_output, prompt_template
    )
    logger.info(
        "Done: Extracting structured output from Junior output using LLM models"
    )
    return llm_extracted_output


def extract_stream_conditions_data_all_equipment(
    document_id, model_name, asset_name_list
):
    """Extracting stream conditions of all the stream/commodity flows
    across the equipments in process narrative data."""
    logger.info(
        """Init: Extracting stream conditions of all the stream/commodity flows
        across the equipments in process narrative data."""
    )
    stream_conditions_output = ""
    # junior_data = []
    for equipment_name in asset_name_list:
        equipment_section_junior_output = _extracted_junior_data_for_a_query(
            model_name, equipment_name, document_id
        )
        if equipment_section_junior_output:
            query_extract_stream_data = _extract_stream_conditions(
                model_name, equipment_name, equipment_section_junior_output
            )
            logger.info(f"Extracted stream flow data for equipment {equipment_name}")
            # junior_data.append(equipment_section_junior_output)
            stream_conditions_output += "\n" + str(query_extract_stream_data)

    # save_json_local(
    #     "data/local/mafpp/process_narrative/18_dec/1/4.junior_data.txt",
    #     junior_data,
    # )
    logger.info(
        """Done: Extracting stream conditions of all the stream/commodity flows
        across the equipments in process narrative data."""
    )
    return stream_conditions_output


async def get_data(
    input_files_path,
    model_name,
    adm_json_path,
    save_to_local=False,
):
    """Get data"""

    bucket_name = input_files_path.get("bucket_name")
    document_id = input_files_path.get("document_id")
    plant_id = input_files_path.get("plant_id")

    asset_table_list_path = (
        f"{plant_id}/documents/process_narrative/{document_id}/assets_table.csv"
    )

    await save_process_equipment_index(bucket_name, plant_id, asset_table_list_path)

    asset_name_list = await get_asset_names_from_s3(bucket_name, asset_table_list_path)
    stream_data_paragraph = extract_stream_conditions_data_all_equipment(
        document_id, model_name, asset_name_list
    )

    if stream_data_paragraph:
        stream_data_path = adm_json_path.replace("adm.json", "stream_data.txt")
        await save_data(
            stream_data_path, stream_data_paragraph, save_to_local, bucket_name
        )

    # stream_data_paragraph_path = r"data\local\mafpp\process_narrative\1
    # 8_dec\1\3.PROCESS_NARRATIVE.stream_data.txt"
    # with open(stream_data_paragraph_path, "r", encoding="utf-8") as file:
    #     stream_data_paragraph = file.read()

    # connection_path = r"tests\test_data\mafpp\inputs\2p&id_source_destination_connection.json"
    # with open(connection_path, "r", encoding="utf-8") as file:
    #     connection_json = json.load(file)
    stream_data_structured = extracted_structured_data_wrapper(
        model_name, stream_data_paragraph
    )
    json_data = {
        "meta_data": {},
        "connections": [],
    }
    if stream_data_structured:
        json_data = get_process_narrative_adm(
            json_data, stream_data_structured, document_id
        )
        await save_data(adm_json_path, json_data, save_to_local, bucket_name)


async def save_data(path, stream_data, save_to_local, bucket_name):
    """Handles the saving of stream data to local or Storage."""
    storage_type = "local" if save_to_local else "storage"
    logger.info(f"Saving stream data to {storage_type}")
    await upload_file_to_storage(
        bucket_name,
        path,
        json.dumps(stream_data).encode("utf-8"),
    )
