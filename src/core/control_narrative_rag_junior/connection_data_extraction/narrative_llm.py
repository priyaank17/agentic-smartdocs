"""
This module contains the functions for extracting narrative data from a PDF file using OpenAI."""

# pylint: disable=no-name-in-module
import json
import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from src.utils.log import logger
from src.utils.llm_models.get_llm import get_llm_model


def get_prompt(prompt_path):
    """Read and return the prompt text from a file."""
    logger.info(f"Init: Reading prompt from {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_text = file.read()
    return prompt_text


def extract_json_from_text(text):
    """Extract JSON from a given text."""
    # Attempt to match either a JSON object or list
    json_match = re.search(r"\[.*\]|\{.*\}", text, re.DOTALL)

    if json_match:
        json_string = json_match.group(0)
        try:
            # If we found a JSON object, wrap it in a list if it's not already
            if json_string.startswith("{") and json_string.endswith("}"):
                json_string = f"[{json_string}]"
            data = json.loads(json_string)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return None
    else:
        logger.error("No JSON found in the text.")
        return None


def get_controller_data(model_name, controller_text, prompt_template):
    """Use OpenAI API to identify controller and equipment_name."""
    logger.info("Init: Identifying controller and equipment_name")
    result = control_narrative_llm_extraction(model_name, controller_text, prompt_template)
    logger.info("Done: Identifying controller and equipment_name")
    return result


def get_control_loop_data(model_name, controller_text, prompt_template):
    """Use OpenAI API to identify controller, transmitter,  control_valve and equipment_name."""
    logger.info("Init: Identifying controller, transmitter,  control_valve and equipment_name")
    result = control_narrative_llm_extraction(model_name, controller_text, prompt_template)
    logger.info("Done: Identifying controller, transmitter,  control_valve and equipment_name")
    return result


def control_narrative_llm_extraction(model_name, narrative_text_string, prompt_template):
    """Get prompt template and response from OpenAI API using LangChain."""
    logger.info("Init: Extracting narrative data using LLM models")
    llm = get_llm_model(model_name=model_name)
    prompt = PromptTemplate(
        input_variables=["narrative_text_string"], template=prompt_template
    )
    name_chain = LLMChain(llm=llm, prompt=prompt)
    inputs = {
        "narrative_text_string": narrative_text_string,
    }
    response = name_chain(inputs=inputs)
    result_string = response["text"].replace("```json", "").replace("`", "")
    # print("LLM response: ", result_string)
    result_object = extract_json_from_text(result_string)
    logger.info("Done: Extracting narrative data.")
    return result_object
