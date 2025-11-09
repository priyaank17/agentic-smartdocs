"""Extract narrative data from pdf file."""

import json
from dotenv import load_dotenv
from src.utils.log import logger
from src.control_narrative_rag_junior.connection_data_extraction.narrative_llm import (
    get_prompt,
    get_control_loop_data,
    get_controller_data,
)
from src.prompts.prompt import (
    CONTROL_NARRATIVE_CONTROL_LOOPS_PROMPT_RAG_JUNIOR_PATH,
    CONTROL_NARRATIVE_CONTROLLER_PROMPT_RAG_JUNIOR_PATH,
)
from src.utils.get_junior_response import (
    get_document_data_from_junior_app_runner,
)
from src.utils.get_equipment_index import save_process_equipment_index
from src.data_sheets.constant import (
    get_asset_details_from_s3,
)

load_dotenv()


def _extracted_junior_data_for_a_query(model_name, document_id, question):
    """Extract narrative data using Junior API"""
    logger.info("Init: Extracting narrative data using Junior API")
    junior_extracted_output = get_document_data_from_junior_app_runner(
        model_name, question, [], document_id
    )
    if junior_extracted_output.status_code == 200:
        try:
            response_content = junior_extracted_output.content.decode("utf-8")
            response_json = json.loads(response_content)
            answer = response_json["output"]["answer"]
            logger.info("Done: Extracting narrative data using Junior")
            return answer
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing response: {e}")
    else:
        logger.error(
            f"Request failed with status code: {junior_extracted_output.status_code}"
        )
    return None


def _extract_controllers_for_asset_junior(model_name, document_id, asset_name):
    """Extract controllers for a specific asset."""
    controller_question = f"In {asset_name}, list all controllers present."
    return _extracted_junior_data_for_a_query(
        model_name, document_id, controller_question
    )


def _extract_control_loops_for_asset_junior(
    model_name, document_id, asset_name, controller_key
):
    """Extract control loops for a specific asset."""
    control_loop_question = f"""In {asset_name}, for controller {controller_key},
    specify the transmitter tags that senses its process variable with proper description,
    and also specify the control valve tags which adjusts to maintain the desired position
    with proper description. Also describe the controller {controller_key}"""
    junior_control_loop_output = _extracted_junior_data_for_a_query(
        model_name, document_id, control_loop_question
    )
    return junior_control_loop_output


def get_extracted_data_for_all_query(document_id, model_name, asset_name_list):
    """Extract Extraction of control loops of all
    the assets in control narrative data.."""
    logger.info(
        "Init: Extracting control loops of all the assets in control narrative data."
    )
    output_json_data = []
    junior_data = {}
    control_loop_junior_data = {}
    controller_json_data = []
    for asset_name in asset_name_list:
        junior_controller_output = _extract_controllers_for_asset_junior(
            model_name, document_id, asset_name
        )
        logger.info(f"junior_controller_output {junior_controller_output}")
        if junior_controller_output:
            controller_text = f"""{asset_name}: {junior_controller_output}"""
            prompt_template = get_prompt(
                CONTROL_NARRATIVE_CONTROLLER_PROMPT_RAG_JUNIOR_PATH
            )
            controller_data = get_controller_data(
                model_name, controller_text, prompt_template
            )
            junior_data[f"{asset_name}"] = junior_controller_output
            controller_json_data.extend(controller_data)
            logger.info(f"controller_data {controller_data}")
            if controller_data:
                controllers = controller_data[0].get("controller", {})
                for key, _ in controllers.items():
                    junior_control_loop_output = _extract_control_loops_for_asset_junior(
                        model_name, document_id, asset_name, key
                    )
                    logger.info(
                        f"junior_control_loop_output {junior_control_loop_output}"
                    )
                    control_loop_junior_data[f"{asset_name}_{key}"] = (
                        junior_control_loop_output
                    )
                    prompt_template_control_loop = get_prompt(
                        CONTROL_NARRATIVE_CONTROL_LOOPS_PROMPT_RAG_JUNIOR_PATH
                    )
                    control_loop_text = f"""
                    {asset_name} (controller {key}): {junior_control_loop_output}
                    """
                    control_loop_data = get_control_loop_data(
                        model_name,
                        control_loop_text,
                        prompt_template_control_loop,
                    )
                    if control_loop_data:
                        logger.info(f"control_loop_data {control_loop_data}")
                        output_json_data.extend(control_loop_data)
        logger.info(
            "Done: Extraction of control loops of all "
            "the assets in control narrative data."
        )
    # _save_control_loop_local(
    #     junior_data=junior_data,
    #     controller_json_data=controller_json_data,
    #     output_json_data=output_json_data,
    #     control_loop_junior_data=control_loop_junior_data,
    # )
    return output_json_data


def _save_control_loop_local(
    junior_data=None,
    controller_json_data=None,
    output_json_data=None,
    control_loop_junior_data=None,
):
    """Save the output to a JSON file."""
    _save_json_local(
        "data/local/mafpp/control_narrative/1_dec/2.controller_junior_data.json",
        junior_data,
    )
    _save_json_local(
        "data/local/mafpp/control_narrative/1_dec/2.controller_llm_data.json",
        controller_json_data,
    )
    _save_json_local(
        "data/local/mafpp/control_narrative/1_dec/2.control_loop_data.json",
        output_json_data,
    )
    _save_json_local(
        "data/local/mafpp/control_narrative/1_dec/2.control_loop_junior_data.json",
        control_loop_junior_data,
    )


def _save_json_local(output_path, output):
    """Save the output to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)


async def get_control_loops_data(bucket_name, plant_id, document_id, model_name):
    """Get data"""
    logger.info("Init: Extraction of control loops of all the assets in control narrative data.")
    asset_table_list_path = (
        f"{plant_id}/documents/control_narrative/{document_id}/assets_table.csv"
    )
    await save_process_equipment_index(bucket_name, plant_id, asset_table_list_path)
    asset_name_list = await get_asset_details_from_s3(bucket_name, asset_table_list_path)
    control_loop_data = get_extracted_data_for_all_query(
        document_id, model_name, asset_name_list
    )
    logger.info(
        "Done: Extraction of control loops of all "
        "the assets in control narrative data."
    )
    return control_loop_data
