"""This module is used to extract property name from narrative text"""

# pylint: disable=no-name-in-module
from langchain_community.callbacks.manager import get_openai_callback
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from src.utils.log import logger
from src.data_sheets.sheets_table_extraction.prompt_info import (
    update_prompt_information,
)
from src.utils.llm_models.get_llm import get_llm_model

load_dotenv()
MODEL_NAME = "gpt-4"


def get_prompt_template_name_and_response(
    prompt_text, llm, narrative_text, property_name_list
):
    """Get prompt template name and response from OpenAI API."""
    prompt_template_name = PromptTemplate(
        input_variables=["property_name_list", "narrative_text_string"],
        template=prompt_text,
    )
    name_chain = LLMChain(llm=llm, prompt=prompt_template_name)
    inputs = {
        "narrative_text_string": narrative_text,
        "property_name_list": property_name_list,
    }
    with get_openai_callback() as cb_response:
        response = name_chain(inputs=inputs)
    return prompt_template_name, cb_response, response


def execute_prompt_extraction(
    prompt_text, llm, narrative_text, prompt_token_path, property_name_list
):
    """Execute prompt extraction."""
    logger.info("INIT: execute_prompt_extraction function initialized")
    prompt_template_name, cb_response, response = get_prompt_template_name_and_response(
        prompt_text, llm, narrative_text, property_name_list
    )
    result_string = response["text"].replace("```json", "").replace("`", "")
    update_prompt_information(prompt_template_name, cb_response, prompt_token_path)
    logger.info("DONE: execute_prompt_extraction function completed")
    return result_string


def chunks(data, n):
    """Yield successive n-sized chunks from data."""
    for i in range(0, len(data), n):
        yield data[i : i + n]


def get_prompt(prompt_path):
    """Read and return the prompt text from a file."""
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_text = file.read()
    return prompt_text


def extract_property_names_llm(
    narrative_text, results, property_name_list, prompt_config
):
    """Extract property names using LLM."""
    logger.info("INIT: Extract Property name Using LLM function initialized")
    prompt_text = prompt_config["prompt_text"]
    llm = prompt_config["llm"]
    prompt_token_path = prompt_config["prompt_token_path"]
    result_object = execute_prompt_extraction(
        prompt_text=prompt_text,
        llm=llm,
        narrative_text=narrative_text,
        prompt_token_path=prompt_token_path,
        property_name_list=property_name_list,
    )
    results.append(result_object)
    return result_object


def retrieve_property_names_using_llm(
    plant_id, data_sheet_text_list, prompt_path, property_name_list
):
    """Retrieve property names using LLM."""
    logger.info("INIT: Extract Property name Using LLM function initialized")
    prompt_token_path = f"{plant_id}/documents/data_sheet"
    prompt_text = ""
    prompt_text = get_prompt(prompt_path)
    llm = get_llm_model(model_name=MODEL_NAME)
    results = None
    chunk_results = []
    prompt_config = {
        "prompt_text": prompt_text,
        "llm": llm,
        "prompt_token_path": prompt_token_path,
    }
    extract_property_names_llm(
        data_sheet_text_list, chunk_results, property_name_list, prompt_config
    )
    results = chunk_results[0]
    logger.info("DONE: Extract Property name Using LLM function completed")
    return results
