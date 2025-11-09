"""Extract narrative data from pdf file."""

import json
from dotenv import load_dotenv
from src.utils.log import logger

from src.utils.s3_download_upload import (
    load_json_from_storage,
)
from src.utils.get_source_destination import (
    process_equipment_connectivity,
)
from src.process_narrative_rag_junior.connection_data_extraction.narrative_llm import (
    get_prompt,
    llm_extraction,
)
from src.utils.storage_utils import (
    upload_file_to_storage,
    fetch_file_via_adapter
)
from src.process_narrative_rag_junior.connection_data_extraction import (
    generate_process_narrative_adm,
)
from src.utils.get_junior_response import (
    get_document_data_from_junior_app_runner,
)

from src.prompts.prompt import PROCESS_NARRATIVE_PROMPT_RAG_JUNIOR_PATH

get_process_narrative_adm = generate_process_narrative_adm.get_process_narrative_adm

load_dotenv()


def _extracted_junior_data_for_a_query(model_name, connection, document_id):
    """Extract narrative data using Junior API"""
    logger.info("Init: Extracting narrative data using Junior API")
    sources_asset_name = connection.get("source_asset_name")
    destination_asset_name = connection.get("destination_asset_name")
    api_input = (
        f"Give me the pressure, temperature and flowrate of stream "
        f"or gas or liquid flowing from {sources_asset_name} to {destination_asset_name}"
    )
    # api_input = (
    #     f"what is the flowrate, temperature and pressure of the flow between "
    #     f"{sources_asset_name} and {destination_asset_name}?"
    # )
    junior_extracted_output = get_document_data_from_junior_app_runner(
        model_name, api_input, [], document_id
    )
    if junior_extracted_output.status_code == 200:
        try:
            response_content = junior_extracted_output.content.decode("utf-8")
            response_json = json.loads(response_content)
            answer = response_json["output"]["answer"]
            logger.info(f"Done: Extracting narrative data using Junior: {answer}")
            return answer
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing response: {e}")
    else:
        logger.error(
            f"Request failed with status code: {junior_extracted_output.status_code}"
        )
    return None


def _extracted_structured_data_for_a_query(model_name, connection, junior_paragraph):
    """Extract structured output using LLM models."""
    logger.info(
        "Init: Extracting structured output from junior output using LLM models"
    )
    prompt_template = get_prompt(PROCESS_NARRATIVE_PROMPT_RAG_JUNIOR_PATH)
    sources_asset_name = connection.get("source_asset_name")
    destination_asset_name = connection.get("destination_asset_name")
    llm_query = (
        f"source_asset_name: {sources_asset_name}\n"
        f"destination_asset_name: {destination_asset_name}"
    )
    llm_extracted_output = llm_extraction(
        model_name, junior_paragraph, llm_query, prompt_template
    )
    logger.info(
        "Done: Extracting structured output from Junior output using LLM models"
    )
    return llm_extracted_output


def _get_extracted_data_for_all_query(
    document_id, model_name, pid_source_destination_connection_data
):
    """Extract Extraction of stream conditions of all
    the queries(connections) in process narrative data.."""
    logger.info(
        "Init: Extracting stream conditions of all the queries in process narrative data."
    )
    output = []
    # junior_data = []
    for connection in pid_source_destination_connection_data:
        junior_output = _extracted_junior_data_for_a_query(
            model_name, connection, document_id
        )
        if junior_output:
            query_extract_data = _extracted_structured_data_for_a_query(
                model_name, connection, junior_output
            )
            logger.info(f"Extracted data: {query_extract_data}")
            # junior_data.append(junior_output)
            output.extend(query_extract_data)
    logger.info(
        "Done: Extraction of stream conditions of all "
        "the queries(connections) in process narrative data."
    )
    # save_json_local(
    #     "data/local/mafpp/process_narrative/test_output/7_nov/2.junior_data.txt",
    #     junior_data,
    # )
    return output


async def get_pid_source_destination_connection_data(
    bucket_name, plant_id, pnid_connections_json_path, local_input_files=False
):
    """Load PID source-destination connection data"""
    if local_input_files:
        pid_source_destination_connection_data = await fetch_file_via_adapter(
            "", pnid_connections_json_path
        )
    else:
        await process_equipment_connectivity(
            bucket_name, plant_id, pnid_connections_json_path
        )
        pid_source_destination_connection_data = await load_json_from_storage(
            bucket_name, pnid_connections_json_path
        )

    if pid_source_destination_connection_data is None:
        logger.error(
            "PID source-destination connection data is either unavailable or empty"
        )
    return pid_source_destination_connection_data


async def get_data(
    input_files_path,
    model_name,
    adm_json_path,
    save_to_local=False,
    local_input_files=False,
):
    """Get data"""
    pid_connections_json_path = input_files_path.get(
        "pid_source_destination_connection_path"
    )
    bucket_name = input_files_path.get("bucket_name")
    plant_id = input_files_path.get("plant_id")
    document_id = input_files_path.get("document_id")
    pid_source_destination_connection_data = (
        await get_pid_source_destination_connection_data(
            bucket_name, plant_id, pid_connections_json_path, local_input_files
        )
    )

    json_data = {
        "meta_data": {},
        "connections": [],
    }

    connection_data = _get_extracted_data_for_all_query(
        document_id, model_name, pid_source_destination_connection_data
    )
    if connection_data:
        json_data = get_process_narrative_adm(json_data, connection_data, document_id)
        storage_type = "local" if save_to_local else "storage"
        logger.info(
            f"Saving detailed process narrative to {storage_type} in {adm_json_path}"
        )
        await upload_file_to_storage(
            bucket_name,
            adm_json_path,
            json.dumps(json_data).encode("utf-8"),
        )
