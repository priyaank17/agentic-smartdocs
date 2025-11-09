"""
This module contains the functions for extracting narrative data from a PDF file using OpenAI."""

# pylint: disable=no-name-in-module
import json
import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from src.utils.llm_models.get_llm import get_llm_model
from src.utils.log import logger


def get_prompt(prompt_path):
    """Read and return the prompt text from a file."""
    logger.info(f"Init: Reading prompt from {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_text = file.read()
    return prompt_text


def extract_json_from_text(text):
    """Extract JSON from a given text."""
    # json_match = re.search(r'\[\s*{.*?}\s*\]', text, re.DOTALL)
    json_match = re.search(r"\[.*\]", text, re.DOTALL)

    if json_match:
        json_string = json_match.group(0)
        try:
            data = json.loads(json_string)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return None
    else:
        logger.error("No JSON found in the text.")
        return None


def llm_extraction(model_name, narrative_text_string, query, prompt_template):
    """Get prompt template and response from OpenAI API using LangChain."""
    logger.info(f"Init: Extracting narrative data using LLM models for a {query}")
    llm = get_llm_model(model_name=model_name)
    prompt = PromptTemplate(
        input_variables=["narrative_text_string", "query"], template=prompt_template
    )
    name_chain = LLMChain(llm=llm, prompt=prompt)
    inputs = {
        "narrative_text_string": narrative_text_string,
        "query": query,
    }
    response = name_chain(inputs=inputs)
    result_string = response["text"].replace("```json", "").replace("`", "")
    # print(result_string)
    result_object = extract_json_from_text(result_string)
    logger.info("Done: Extracting narrative data.")
    return result_object
