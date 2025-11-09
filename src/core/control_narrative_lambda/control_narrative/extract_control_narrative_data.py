"""This script is used to extract the control narrative data from the process narrative"""

# pylint: disable=no-name-in-module

import json
from concurrent.futures import ThreadPoolExecutor
from langchain_community.callbacks.manager import get_openai_callback
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from src.utils.log import logger
from src.core.utils.storage_utils import upload_file_to_storage

# from .schema_validation import schema_validation
from src.core.control_narrative_lambda.control_narrative.get_id import (
    add_narrative_id,
    flatten,
    add_id,
)
from src.core.control_narrative_lambda.constant import (
    prompt_control_loop,
    prompt_instrument,
)
from src.core.utils.llm_models.get_llm import get_llm_model
from src.core.control_narrative_lambda.postprocessing.postprocess import (
    postprocess_control_narrative,
)
from src.core.utils.s3_download_upload import read_csv_from_storage
from src.core.control_narrative_lambda.control_narrative.extract_ocr import (
    create_narrative_csv,
)

load_dotenv()
MODEL_NAME = "gpt-4"


def _chunks(data, n):
    """
    Generates chunks of size `n` from the given `data`.
    """
    for i in range(0, len(data), n):
        yield data[i : i + n]


def _get_prompt_template_name_and_response(prompt_text, llm, control_narrative_text):
    """
    Retrieves a prompt template name and response from the OpenAI Chat API based
    on the given prompt text, language model, and control narrative text.
    """
    prompt_template_name = PromptTemplate(
        input_variables=["control_narrative_text_string"],
        template=prompt_text,
    )
    name_chain = LLMChain(llm=llm, prompt=prompt_template_name)
    with get_openai_callback() as cb_response:
        response = name_chain(
            {
                "control_narrative_text_string": control_narrative_text,
            }
        )
    return prompt_template_name, cb_response, response


def _extract_control_data_by_prompt(extract_control_data_by_prompt_args):
    """
    Extracts control data by prompt.
    Returns:
        dict: The extracted control data as a dictionary.
    """
    (
        prompt_text,
        llm,
        id_number,
        control_narrative_text,
    ) = extract_control_data_by_prompt_args
    logger.info("INIT: Extract_Data_By_Prompt function initialized")
    _, _, response = _get_prompt_template_name_and_response(
        prompt_text, llm, control_narrative_text
    )
    result_string = response["text"].replace("```json", "").replace("```", "")
    result_object = json.loads(result_string)
    add_narrative_id(result_object, id_number)
    logger.info("DONE: Extract_Data_By_Prompt function completed")
    return result_object


def _process_control(process_control_args):
    """
    Process a control narrative paragraph by extracting control data using a prompt.
    """
    (
        index,
        id_number,
        control_narrative_text,
        number_of_paragraphs,
        prompt_config,
        results,
    ) = process_control_args
    logger.info(f"INIT:Processing paragraph {index + 1} of (id {id_number})")
    prompt_text = prompt_config.get("prompt_text")
    llm = prompt_config.get("llm")
    result_object = _extract_control_data_by_prompt(
        (
            prompt_text,
            llm,
            id_number,
            control_narrative_text,
        )
    )
    results.append(result_object)
    logger.info(
        f"DONE: Processing paragraph {index + 1} of "
        f"(id {id_number}) from total {number_of_paragraphs} paragraphs)"
    )
    return result_object


def get_prompt(control_narrative_prompt_path):
    """
    Reads the contents of a file specified by `control_narrative_prompt_path`
    and returns the contents as a string.

    Parameters:
        control_narrative_prompt_path (str): The path to the file to be read.

    Returns:
        str: The contents of the file as a string.
    """
    with open(control_narrative_prompt_path, encoding="utf-8") as file:
        prompt_text = file.read()
    return prompt_text


async def _extract_instrument_data(
    narrative_text_info, bucket_name, key_aggregated_instruments, local_path
):
    """
    Extracts instrument data from a list of control narrative text.
    """
    logger.info("INIT: Extract Instrument Data function initialized")
    prompt_text = ""
    prompt_text = prompt_instrument
    results = _extract_data(narrative_text_info, prompt_text)
    add_id("instrument_", results)
    await save_json(results, bucket_name, key_aggregated_instruments, local_path)
    logger.info("DONE: Extract Instrument Data function completed")


async def save_json(results, bucket_name, key_aggregated, local_path):
    """Save instrument data to S3."""
    if local_path:
        with open(key_aggregated, "w", encoding="utf-8") as f:
            json.dump(results, f)
        return
    await upload_file_to_storage(
        bucket_name, key_aggregated, json.dumps(results)
    )

    logger.info(f"The result object is written to {bucket_name}/{key_aggregated}")


def _extract_data(narrative_text_info, prompt_text):
    """Extract control narrative data using LLM"""
    control_narrative_text_list = narrative_text_info["text"]
    id_list = narrative_text_info["id"]
    number_of_paragraphs = len(control_narrative_text_list)
    llm = get_llm_model(model_name=MODEL_NAME)
    results = []
    prompt_config = {
        "prompt_text": prompt_text,
        "llm": llm,
    }
    paired_list = list(zip(id_list, control_narrative_text_list))
    for control_narrative_chunk in _chunks(list(enumerate(paired_list)), 4):
        # pylint: disable=cell-var-from-loop
        chunk_results = []
        with ThreadPoolExecutor() as executor:
            chunk_results = list(
                executor.map(
                    lambda item: _process_control(
                        (
                            item[0],
                            item[1][0],
                            item[1][1],
                            number_of_paragraphs,
                            prompt_config,
                            chunk_results,
                        )
                    ),
                    control_narrative_chunk,
                )
            )
        results.extend(chunk_results)
    results = flatten(results)
    return results


async def _extract_control_loops_data(
    narrative_text_info,
    bucket_name,
    key_aggregated_control_loops,
    local_path,
):
    """
    Extracts control loops data from a list of control narrative text.
    """
    logger.info("INIT: Extract Control Loops Data function initialized")
    prompt_text = ""
    prompt_text = prompt_control_loop
    results = _extract_data(narrative_text_info, prompt_text)
    add_id("control_loop_", results)
    await save_json(results, bucket_name, key_aggregated_control_loops, local_path)
    logger.info("DONE: Extract Control Loops Data function completed")


async def extract_control_narrative_data(
    bucket_name,
    input_data_path,
    reconciled_control_loops_path,
    key_aggregated_info,
    local_path=False,
):
    """
    Extracts control narrative data from a CSV file in an S3 bucket.
    """
    logger.info("INIT: Extract Control Narrative Data function initialized")
    key_aggregated_control_loops = key_aggregated_info["key_aggregated_control_loops"]
    key_aggregated_instruments = key_aggregated_info["key_aggregated_instruments"]
    await create_narrative_csv(bucket_name, input_data_path)
    narrative_csv_path = input_data_path.replace(
        "input_data.json", "control_narrative.csv"
    )
    df = await read_csv_from_storage(bucket=bucket_name, path=narrative_csv_path)
    n = df["id"].max()

    narrative_text_info = await read_csv_from_storage(bucket=bucket_name, path=narrative_csv_path)
    await _extract_instrument_data(
        narrative_text_info,
        bucket_name,
        key_aggregated_instruments,
        local_path,
    )

    await _extract_control_loops_data(
        narrative_text_info,
        bucket_name,
        key_aggregated_control_loops,
        local_path,
    )
    await postprocess_control_narrative(
        key_aggregated_control_loops=key_aggregated_control_loops,
        bucket_name=bucket_name,
        reconciled_control_loops_path=reconciled_control_loops_path,
        narrative_text=narrative_text_info,
        n=n,
        local_path=local_path,
    )

    logger.info("DONE: Extract Control Narrative Data function completed")
