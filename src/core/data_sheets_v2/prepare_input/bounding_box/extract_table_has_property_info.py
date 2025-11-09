"""Extract table has property information from the image using llm."""

from src.utils.log import logger
from src.utils.llm_models.get_llm import get_llm_model
from src.utils.llm_models.llm_utils import retry_with_backoff
from src.data_sheets_v2.extract_table_data.image_utlis import (
    encode_image_2,
    get_cropped_image,
)
from src.data_sheets_v2.prepare_input.bounding_box.get_prompt import (
    get_prompt_table_info,
)
from src.utils.s3_download_upload import (
    load_into_memory,
)
from src.utils.json_utils import extract_json_from_text


def call_llm(llm, message):
    """Call LLM API."""
    ai_message = llm.invoke(message)
    return ai_message.content


def extract_table_has_property_info(image, model_name):
    """Extract table has property information from the image using LLM."""
    logger.info("""INIT: Extracting data from image with property table""")
    llm = get_llm_model(model_name=model_name)
    base64_image = encode_image_2(image)
    message = get_prompt_table_info(base64_image)
    output = retry_with_backoff(call_llm, llm, message)
    result_string = output.replace("```json", "").replace("`", "")
    logger.info(f"llm response: {result_string}")
    result_object = extract_json_from_text(result_string)
    logger.info("""DONE: Data extracted from image with property table""")
    if not isinstance(result_object, list):
        raise ValueError("LLM response is not a list. Expected a list with one object.")
    if len(result_object) != 1:
        logger.warning(
            "LLM response More than one object in the list. "
            "Expected a list with one object."
        )
    return result_object


def extract_table_info(image, model_name):
    """Extract table name and "has property" information from the image using LLM."""
    logger.info("""INIT: Extracting data from image with property table""")
    llm = get_llm_model(model_name=model_name)
    base64_image = encode_image_2(image)
    message = get_prompt_table_info(base64_image)
    output = retry_with_backoff(call_llm, llm, message)
    print(f"output: {output}")
    result_string = output.replace("```json", "").replace("`", "")
    logger.info(f"llm response: {result_string}")
    result_object = extract_json_from_text(result_string)
    logger.info("""DONE: Data extracted from image with property table""")
    if not isinstance(result_object, list):
        raise ValueError("LLM response is not a list. Expected a list with one object.")
    if len(result_object) != 1:
        logger.warning(
            "LLM response More than one object in the list. "
            "Expected a list with one object."
        )
    return result_object


async def get_table_has_property_info(
    bucket_name, image_path, table_bounding_box, model_name="gpt-4o"
):
    """
    Extracts table has property information from the image using the bounding box.
    """
    logger.info("INIT: Extracting table has property information.")
    try:
        # Simulate extraction logic
        # In a real scenario, this would involve analyzing the image and bounding box
        # to determine if the table has specific properties.
        image_data = await load_into_memory(bucket_name, image_path)
        cropped_image = get_cropped_image(image_data, table_bounding_box)
        table_info = extract_table_has_property_info(cropped_image, model_name)

        logger.info("DONE: Extracted table has property information.")
        return table_info
    except Exception as e:
        logger.error(f"Failed to extract table has property info: {str(e)}")
        raise


async def get_table_info_llm(
    bucket_name, image_path, table_bounding_box, model_name="gpt-4o"
):
    """
    Extracts table name from the image using the bounding box.
    """
    logger.info("INIT: Extracting table name from image.")
    try:
        # to determine the table name.
        image_data = await load_into_memory(bucket_name, image_path)
        cropped_image = get_cropped_image(image_data, table_bounding_box)
        table_info = extract_table_info(cropped_image, model_name)
        print(f"table_info: {table_info}")
        logger.info("DONE: Extracted table name.")
        return table_info
    except Exception as e:
        logger.error(f"Failed to extract table name: {str(e)}")
        raise
