"""Extract narrative data from pdf file."""

import json
from dotenv import load_dotenv
from src.utils.log import logger
from src.process_narrative_rag_junior.extract_equipment_operating_conditions.narrative_llm import (
    get_prompt,
    llm_extraction,
)
from src.process_narrative_rag_junior.get_junior_response import (
    load_junior_input,
)
from src.utils.storage_utils import (
    upload_file_to_storage
)
from src.utils.get_junior_response import (
    get_document_data_from_junior_app_runner,
)
from src.prompts.prompt import PROCESS_NARRATIVE_EQUIPMENT_PROMPT_RAG_JUNIOR_PATH
from src.prompts.junior_input_prompt import (
    PROCESS_NARRATIVE_EQUIPMENT_OPERATING_CONDITIONS_JUNIOR_INPUT_PATH,
)
from src.process_narrative_rag_junior.extract_equipment_operating_conditions import (
    generate_process_narrative_equipment_adm,
)
from src.utils.get_equipment_index import save_process_equipment_index

from src.data_sheets.constant import get_asset_names_from_s3

get_process_narrative_adm = (
    generate_process_narrative_equipment_adm.get_process_narrative_adm
)
load_dotenv()


def extracted_junior_data_for_a_query(model_name, equipment_name, document_id):
    """Extract narrative data using Junior API"""
    logger.info("Init: Extracting narrative data using Junior API")
    junior_input_path = (
        PROCESS_NARRATIVE_EQUIPMENT_OPERATING_CONDITIONS_JUNIOR_INPUT_PATH
    )
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


def extracted_structured_data_for_a_query(model_name, equipment_name, junior_paragraph):
    """Extract structured output using LLM models."""
    logger.info(
        "Init: Extracting structured output from junior output using LLM models"
    )
    prompt_template = get_prompt(PROCESS_NARRATIVE_EQUIPMENT_PROMPT_RAG_JUNIOR_PATH)
    llm_query = f"equipment_name: {equipment_name}"
    llm_extracted_output = llm_extraction(
        model_name, junior_paragraph, llm_query, prompt_template
    )
    logger.info(
        "Done: Extracting structured output from Junior output using LLM models"
    )
    return llm_extracted_output


def get_extracted_data_for_all_query(document_id, model_name, asset_name_list):
    """Extract Extraction of operating conditions of all
    the queries(equipments) in process narrative data.."""
    logger.info(
        "Init: Extracting operating conditions of all the queries in process narrative data."
    )
    output = []
    # junior_data = []
    for equipment_name in asset_name_list:
        junior_output = extracted_junior_data_for_a_query(
            model_name, equipment_name, document_id
        )
        if junior_output:
            query_extract_data = extracted_structured_data_for_a_query(
                model_name, equipment_name, junior_output
            )
            logger.info(f"Extracted data: {query_extract_data}")
            # junior_data.append(junior_output)
            output.extend(query_extract_data)
    logger.info(
        "Done: Extraction of operating conditions of all "
        "the queries(equipments) in process narrative data."
    )
    # save_json_local(
    #     "data/local/mafpp/process_narrative/2_dec/2.operating_data_junior_data.txt",
    #     junior_data,
    # )
    return output


# def save_json_local(output_path, output):
#     """Save the output to a JSON file."""
#     with open(output_path, "w", encoding="utf-8") as json_file:
#         json.dump(output, json_file, ensure_ascii=False, indent=4)


async def get_equipment_operating_data(
    input_files_path,
    model_name,
    adm_json_path,
    save_to_local=False,
):
    """Get data"""
    bucket_name = input_files_path.get("bucket_name")
    plant_id = input_files_path.get("plant_id")
    document_id = input_files_path.get("document_id")

    json_data = {
        "meta_data": {},
        "data": [],
    }
    # equipment_index_json_path = (
    #     f"public/{plant_id}/DOCS/PROCESS_NARRATIVE/{document_id}/equipment_index.json"
    # )
    asset_table_list_path = (
        f"{plant_id}/documents/process_narrative/{document_id}/assets_table.csv"
    )
    await save_process_equipment_index(bucket_name, plant_id, asset_table_list_path)
    asset_name_list = await get_asset_names_from_s3(bucket_name, asset_table_list_path)
    asset_operating_data = get_extracted_data_for_all_query(
        document_id, model_name, asset_name_list
    )
    if asset_operating_data:
        json_data = get_process_narrative_adm(
            json_data, asset_operating_data, document_id
        )
        storage_type = "local" if save_to_local else "storage"
        logger.info(
            f"Data saved successfully to {storage_type} in {adm_json_path}"
        )
        await upload_file_to_storage(
            bucket_name,
            adm_json_path,
            json.dumps(json_data).encode("utf-8"),
        )
        # if save_to_local:
        #     logger.info(f"Saving to local in {adm_json_path}")
        #     save_json_local(adm_json_path, json_data)
        # else:
        #     logger.info(f"Saving to s3 {adm_json_path}")
        #     save_json_to_storage(bucket_name, adm_json_path, json_data)
