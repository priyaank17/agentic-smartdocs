"""Extract data from an image of a table."""

# pylint: disable=broad-exception-caught
import json
import time
import re
from src.utils.llm_models.get_llm import get_llm_model
from src.utils.log import logger
from src.utils.s3_download_upload import (
    load_into_memory,
)
from src.data_sheets_v2.extract_table_data.get_prompt_tables_having_property import (
    get_property_conversion_prompt,
    get_prompt_format_1_v2,
)
from src.data_sheets_v2.extract_table_data.get_prompt_tables_without_property import (
    get_prompt_format_2_v1,
)
from src.data_sheets_v2.extract_table_data.file_io import save_data
from src.data_sheets_v2.postprocessing.postprocess import (
    convert_unicode_to_boolean,
    rename_empty_columns,
)
from src.utils.llm_models.llm_utils import retry_with_backoff
from src.data_sheets_v2.extract_table_data.image_utlis import (
    encode_image_2,
    get_cropped_image,
)
from src.utils.storage_utils import upload_file_to_storage, fetch_file_via_adapter


def _extract_json_from_text(text):
    """
    Extract JSON object(s) from a given text.
    """
    cleaned_data = re.sub(r"//.*", "", text)
    try:
        json_object = json.loads(cleaned_data)
        return json_object
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return None


def _get_property_name(extracted_data):
    """get property names from the extracted data."""
    property_data = extracted_data.get("data")
    if property_data:
        filter_data = [{"Property": item["Property"]} for item in property_data]
        return filter_data
    return []


def _call_llm(llm, message):
    """Call LLM API."""
    ai_message = llm.invoke(message)
    return ai_message.content


def _extract_standard_property_name_data(
    extracted_data, table_name, appearance_number, model_name
):
    """get standard property names from the extracted data."""
    logger.info(
        f"""INIT: Extracting standard property names
                for {table_name}, appearance_number: {appearance_number}"""
    )
    if not extracted_data:
        return None
    llm = get_llm_model(model_name=model_name)
    filter_data = _get_property_name(extracted_data)
    message = get_property_conversion_prompt(filter_data)
    output = retry_with_backoff(_call_llm, llm, message, table_name=table_name)
    result_string = output.replace("```json", "").replace("`", "")
    logger.info(f"llm response: {result_string}")
    result_object = _extract_json_from_text(result_string)
    logger.info(
        f"""DONE: Standard property names extracted
        for {table_name} appearance_number: {appearance_number}"""
    )
    return result_object


def _add_standard_property(data_json, property_mapping):
    """Add standard property names to the data."""
    logger.info("INIT: Adding standard property names to the data.")
    property_dict = {
        item.get("Property", ""): item.get("Standard Property", "")
        for item in property_mapping
    }

    columns = data_json.get("column_names", [])
    columns.insert(0, "Standard Property")
    table_data = data_json.get("data", [])

    for entry in table_data:
        property_name = entry.get("Property", "")
        standard_property = property_dict.get(property_name, "")

        updated_entry = {
            "Standard Property": standard_property,
            "Property": property_name,
        }
        updated_entry.update({k: v for k, v in entry.items() if k != "Property"})

        entry.clear()
        entry.update(updated_entry)
    logger.info("DONE: Standard property names added to the data.")
    return data_json


def _extract_image_data_with_property_table(
    image, table_name, appearance_number, model_name
):
    """Extract data from an image of a table."""
    logger.info(
        f"""INIT: Extracting data from image with property table
          for {table_name}, appearance_number: {appearance_number}"""
    )
    llm = get_llm_model(model_name=model_name)
    base64_image = encode_image_2(image)
    message = get_prompt_format_1_v2(base64_image)
    output = retry_with_backoff(_call_llm, llm, message, table_name=table_name)
    result_string = output.replace("```json", "").replace("`", "")
    logger.info(f"llm response: {result_string}")
    result_object = _extract_json_from_text(result_string)
    logger.info(
        f"""DONE: Data extracted from image with property table
        for {table_name}, appearance_number: {appearance_number}"""
    )
    return result_object


def _extract_image_data_without_property_table(
    image, table_name, appearance_number, model_name
):
    """Extract data from an image of a table."""
    logger.info(
        f"""INIT: Extracting data from image without property table
        for {table_name}, appearance_number: {appearance_number}"""
    )
    llm = get_llm_model(model_name=model_name)
    base64_image = encode_image_2(image)
    message = get_prompt_format_2_v1(base64_image)
    output = retry_with_backoff(_call_llm, llm, message, table_name=table_name)
    result_string = output.replace("```json", "").replace("`", "")
    logger.info(f"llm response: {result_string}")
    result_object = _extract_json_from_text(result_string)
    logger.info(
        f"""DONE: Data extracted from image without property
        table for {table_name}, appearance_number: {appearance_number}"""
    )
    return result_object


def _add_table_details(data_json, table):
    """
    Add page_id, page_number, and parent_table_name to the data JSON
    and reorder them to appear after table_name.
    """

    data_json["table_name"] = table.get("table_name")
    reordered_data = {
        "table_name": table.get("table_name"),
        "table_id": table.get("id"),
        "appearance_number": table.get("appearance_number"),
        "parent_table_name": table.get("parent_table_name"),
        "page_id": table.get("page_id"),
        "page_number": table.get("page_number"),
        **data_json,
    }
    return reordered_data


async def _extract_table(table, model_name, path, bucket, save_local):
    """Extract a single table's data."""
    try:
        table_id = table.get("id")
        page_id = table.get("page_id")
        table_name = table.get("table_name")
        extracted_table_data_json = None

        if not table_name:
            logger.info(f"Skipping table with missing table_name: {table}")
            return None

        table_name = table.get("table_name").lower().replace(" ", "_")
        appearance_number = table.get("appearance_number")
        logger.info(
            f"""INIT: Extracting data for Table ID={table_id},
            Name={table_name}, Appearance Number={appearance_number}"""
        )
        table_has_property = table.get("table_has_property", True)
        bounding_box = table.get("table_bounding_box")
        page_path = f"{path}/{page_id}"
        image_data = await load_into_memory(bucket, page_path)
        cropped_image = get_cropped_image(image_data, bounding_box)

        if table_has_property:
            extracted_table_data = _extract_image_data_with_property_table(
                cropped_image, table_name, appearance_number, model_name
            )
            extracted_standard_property_name = _extract_standard_property_name_data(
                extracted_table_data, table_name, appearance_number, model_name
            )
            if extracted_standard_property_name and extracted_table_data:
                extracted_table_data = _add_table_details(extracted_table_data, table)
                extracted_table_data_json = _add_standard_property(
                    extracted_table_data, extracted_standard_property_name
                )
        else:
            extracted_table_data = _extract_image_data_without_property_table(
                cropped_image, table_name, appearance_number, model_name
            )
            if extracted_table_data:
                extracted_table_data_json = _add_table_details(
                    extracted_table_data, table
                )

        logger.info(
            f"""DONE: Extracted data for Table ID={table_id},
              Name={table_name}, Appearance Number={appearance_number}"""
        )
        if appearance_number is not None and appearance_number > 1:
            table_name = f"{table_name}_{appearance_number}"

        if extracted_table_data_json:
            post_process_data_json = convert_unicode_to_boolean(
                extracted_table_data_json
            )
            post_process_data_json = rename_empty_columns(post_process_data_json)
            await save_data(
                save_local, table_name, path, post_process_data_json, bucket
            )
        else:
            logger.info(f"No table data found for {table_name}")
        return None
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Error processing table: {e}")
        raise


async def _process_tables(table_processing_context, filter_unprocessed=False):
    """Process tables"""
    input_data_path = table_processing_context["input_data_path"]
    input_data = table_processing_context["input_data"]
    model_name = table_processing_context["model_name"]
    bucket = table_processing_context["bucket"]
    save_local = table_processing_context["save_local"]
    document_id = table_processing_context["document_id"]
    plant_id = table_processing_context["plant_id"]
    logger.info("Processing tables...")

    path = f"{plant_id}/documents/data_sheet/{document_id}"
    tables = input_data["tables_data"]
    total_time = 0

    if filter_unprocessed:
        tables_to_process = [
            table for table in tables if not table.get("is_extracted", False)
        ]
    else:
        tables_to_process = tables

    for table in tables_to_process:
        last_request_time = time.time()
        try:
            await _extract_table(table, model_name, path, bucket, save_local)
            table["is_extracted"] = True
        except Exception as e:
            logger.warning(f"Skipping table due to error: {e}")
            continue  # Skip to the next table
        total_time = total_time + time.time() - last_request_time
        if total_time >= 800:
            await upload_file_to_storage(
                bucket, input_data_path, json.dumps(input_data)
            )
            logger.warning(
                f"Processing time exceeded 800 seconds with {total_time:.2f}"
            )
            return None

    await upload_file_to_storage(bucket, input_data_path, json.dumps(input_data))
    logger.info(f"DONE: Table data extraction completed in {total_time:.2f} seconds.")
    return None


async def extract_table_data(input_data_path, table_info, bucket, save_local=False):
    """Extract table data with batch and parallel processing for all tables."""
    logger.info("INIT: Extracting table data.")
    input_data_raw = await fetch_file_via_adapter(bucket, input_data_path)
    # Process all tables and mark them as processed
    model_name = table_info.get("model_name")
    document_id = table_info.get("document_id")
    plant_id = table_info.get("plant_id")
    processing_context = {
        "input_data_path": input_data_path,
        "input_data": input_data_raw,
        "model_name": model_name,
        "bucket": bucket,
        "save_local": save_local,
        "document_id": document_id,
        "plant_id": plant_id,
    }
    await _process_tables(processing_context, filter_unprocessed=False)


async def extract_second_shot_table_data(
    input_data_path, bucket, table_info, save_local=False
):
    """Extract table data for unprocessed tables only."""
    logger.info("INIT: Extracting unprocessed table data.")
    input_data = await fetch_file_via_adapter(bucket, input_data_path)
    model_name = table_info.get("model_name")
    document_id = table_info.get("document_id")
    plant_id = table_info.get("plant_id")

    processing_context = {
        "input_data_path": input_data_path,
        "input_data": input_data,
        "model_name": model_name,
        "bucket": bucket,
        "save_local": save_local,
        "document_id": document_id,
        "plant_id": plant_id,
    }

    # Process only unprocessed tables
    await _process_tables(processing_context, filter_unprocessed=True)


async def extract_table_by_id(input_data_path, bucket, table_id_info, save_local=False):
    """
    Extract a single table by its ID and update the `is_extraction` field.
    """
    table_id = table_id_info.get("table_id")
    document_id = table_id_info.get("document_id")
    plant_id = table_id_info.get("plant_id")
    model_name = table_id_info.get("model_name")
    logger.info(f"INIT: Extracting table with ID: {table_id}")
    try:
        input_data = await fetch_file_via_adapter(bucket, input_data_path)
        path = f"{plant_id}/documents/data_sheet/{document_id}"
        tables = input_data["tables_data"]

        table_to_process = next(
            (table for table in tables if table["id"] == table_id), None
        )

        if not table_to_process:
            logger.error(f"Table with ID {table_id} not found.")
            return

        logger.info(f"Found table: {table_to_process['table_name']}")

        try:
            await _extract_table(table_to_process, model_name, path, bucket, save_local)
            table_to_process["is_extracted"] = True
            logger.info(f"Table with ID {table_id} marked as extracted.")
        except Exception as e:
            logger.error(f"Error extracting table with ID {table_id}: {e}")
            return
        logger.info(f"Table with ID {table_id} marked as extracted.")

        await upload_file_to_storage(bucket, input_data_path, json.dumps(input_data))
        logger.info(f"Updated JSON saved to S3 at {input_data_path}.")
    except Exception as e:
        logger.error(f"Error processing table with ID {table_id}: {e}")
