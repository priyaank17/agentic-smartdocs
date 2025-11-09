"""Prepare input data for table extraction from document intelligence JSON data."""

import re
from src.utils.log import logger
from src.data_sheets_v2.prepare_input.document_intelligence.extract_document_intelligence import (
    get_document_intelligence,
)
from src.utils.storage_utils import (
    list_objects_in_storage,
)
from src.utils.s3_download_upload import load_into_memory, load_json_from_storage
from src.data_sheets_v2.prepare_input.bounding_box.get_bounding_box_region import (
    get_table_from_document_intelligence,
    extract_table_bounding_boxes,
)
from src.data_sheets_v2.prepare_input.landing_ai.vision_extract_input_json import (
    parse_pages,
)


async def get_list_of_page(bucket, path):
    """
    Get a list of page paths from the specified bucket and path.
    """
    all_files_path = await list_objects_in_storage(bucket, path)
    if not all_files_path:
        return []
    files_str = str(all_files_path)
    all_paths = re.findall(r"path='([^']+)'", files_str)
    pattern = re.compile(
        r"^[\w\-]+/documents/data_sheet/[\w\-]+/[\w\-]+\+\d+X\d+\+\d+$"
    )
    filtered_paths = [path for path in all_paths if pattern.match(path)]
    return filtered_paths


async def get_document_intelligence_files(
    bucket_name, image_path, extracted_document_intelligence_pdf_output_path
):
    """
    Get document intelligence files from the specified bucket and path.
    """
    logger.info("INIT: Extracting document intelligence data from file")
    image_bytes = await load_into_memory(bucket_name, image_path)

    await get_document_intelligence(
        bucket_name,
        image_bytes,
        extracted_document_intelligence_pdf_output_path,
        "image_bytes",
    )
    logger.info(
        "DONE: Document intelligence extracted and"
        f"saved to {extracted_document_intelligence_pdf_output_path}"
    )


async def prepare_table_extraction_data(
    bucket_name, data_sheet_folder_path, document_id, plant_id
):
    """
    Main function to extract bounding boxes from document intelligence JSON data.
    This function retrieves the list of pages, processes each page to extract
    document intelligence, and extracts table bounding boxes.
    """
    logger.info("INIT: Get input data for table extraction.")
    input_table_data = []
    input_data = {"meta_data": {}, "table_data": input_table_data}
    image_path_list = await get_list_of_page(bucket_name, data_sheet_folder_path)
    for image_path in image_path_list:
        document_intelligence_image_path = f"{image_path}.ocr.json"
        await get_document_intelligence_files(
            bucket_name,
            image_path,
            document_intelligence_image_path,
        )
        extracted_document_intelligence_json = await load_json_from_storage(
            bucket_name, document_intelligence_image_path
        )

        table_bounding_box = get_table_from_document_intelligence(
            extracted_document_intelligence_json
        )
        table_data = await extract_table_bounding_boxes(
            bucket_name,
            image_path,
            table_bounding_box,
            {
                "page_number": _extract_page_number(image_path),
                "pdf_uuid": document_id,
                "page_id": image_path.split("/")[-1],
                "table_has_property": True,
                "parent_table_name": "",
                "columns": [],
                "is_extracted": False,
                "appearance_number": 1,
                "is_validated": False,
            },
        )
        input_table_data.extend(table_data)
        # break

    input_data["table_data"] = input_table_data
    updated_input_data = _input_meta_data(input_data, document_id, plant_id)
    logger.info("DONE: Extracted input data for table extraction.")
    return updated_input_data


async def prepare_table_extraction_data_vision(
    bucket_name, data_sheet_folder_path, document_id, plant_id
):
    """
    Main function to extract bounding boxes from document intelligence JSON data.
    This function retrieves the list of pages, processes each page to extract
    document intelligence, and extracts table bounding boxes.
    """
    logger.info("INIT: Get input data for table extraction.")
    input_table_data = []
    input_data = {"meta_data": {}, "table_data": input_table_data}
    image_path_list = await get_list_of_page(bucket_name, data_sheet_folder_path)
    input_table_data = await parse_pages(bucket_name, image_path_list)
    input_data["tables_data"] = input_table_data
    updated_input_data = _input_meta_data(input_data, document_id, plant_id)
    logger.info("DONE: Extracted input data for table extraction.")
    return updated_input_data


def _extract_page_number(image_path):
    """
    Extracts the page number from the image path.
    Assumes the page number is the last part after the last '+' in the filename.
    """
    try:
        return image_path.split("/")[-1].split("+")[-1]
    except IndexError:
        return ""


def _input_meta_data(input_data, document_id, plant_id):
    """
    Add metadata to the input data.
    """
    logger.info("INIT: Adding metadata to input data.")
    input_data["meta_data"]["asset_tag"] = ""
    input_data["meta_data"]["asset_class"] = ""
    input_data["meta_data"]["asset_name"] = ""
    input_data["meta_data"]["plant_id"] = plant_id
    input_data["meta_data"]["document_id"] = document_id
    input_data["meta_data"]["document_type"] = "data_sheet"
    logger.info("DONE: Added metadata to input data.")
    return input_data
