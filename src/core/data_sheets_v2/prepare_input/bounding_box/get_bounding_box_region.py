"""Extracts bounding boxes from document intelligence JSON data."""

import uuid
from src.utils.log import logger
from src.data_sheets_v2.prepare_input.bounding_box.extract_table_has_property_info import (
    get_table_has_property_info,
)


def get_table_from_document_intelligence(document_intelligence_json):
    """
    Extracts table bounding boxes from the document intelligence JSON data.
    """
    tables_bb = []
    # Validate JSON structure
    if "analyzeResult" not in document_intelligence_json:
        raise ValueError("Missing 'analyzeResult' in document intelligence JSON")

    if "tables" not in document_intelligence_json["analyzeResult"]:
        return tables_bb  # Return empty list if no tables found

    for table in document_intelligence_json["analyzeResult"]["tables"]:
        # Validate table structure
        if "bounding_regions" not in table or not table["bounding_regions"]:
            continue
        if "polygon" not in table["bounding_regions"][0]:
            continue
        bounding_box = table["bounding_regions"][0]["polygon"]
        tables_bb.append(bounding_box)
    return tables_bb


async def extract_table_bounding_boxes(
    bucket_name, image_path, polygon_list, table_details
):
    """
    Extracts bounding boxes from document intelligence JSON data.
    """
    logger.info("INIT: Extract bounding boxes from document intelligence JSON data.")
    input_table_data = []
    page_number = table_details.get("page_number", None)
    pdf_uuid = table_details.get("pdf_uuid", None)
    page_id = table_details.get("page_id", None)
    table_has_property = table_details.get("table_has_property", True)
    parent_table_name = table_details.get("parent_table_name", "")
    columns = table_details.get("columns", [])
    is_extracted = table_details.get("is_extracted", False)
    appearance_number = table_details.get("appearance_number", 1)
    is_validated = table_details.get("is_validated", False)

    for idx, polygon in enumerate(polygon_list, start=1):
        # Validate polygon structure
        if not isinstance(polygon, list) or len(polygon) < 3:
            logger.warning(
                f"""Skipping invalid polygon at index {idx} on page {page_number}: {polygon}"""
            )
            continue
        if not all(
            isinstance(point, dict) and "x" in point and "y" in point
            for point in polygon
        ):
            logger.warning(
                f"""Skipping invalid polygon points at
                index {idx} on page {page_number}: {polygon}"""
            )
            continue
        table_id = str(uuid.uuid4())
        x_coords = [point["x"] for point in polygon]
        y_coords = [point["y"] for point in polygon]
        # Ensure that the bounding box is valid
        if not x_coords or not y_coords:
            logger.warning(
                f"""Skipping polygon with no coordinates at index {idx}
                on page {page_number}: {polygon}"""
            )
            continue

        table_bounding_box = {
            "x_min": min(x_coords),
            "x_max": max(x_coords),
            "y_min": min(y_coords),
            "y_max": max(y_coords),
        }
        try:
            table_info_llm = await get_table_has_property_info(
                bucket_name, image_path, table_bounding_box
            )
            table_has_property = table_info_llm[0].get("table_has_property", True)
            table_name = table_info_llm[0].get(
                "table_name", "table_" + str(idx) + "_page_" + page_number
            )
        except RuntimeError as e:
            logger.warning(
                f"Failed to extract table property info for table {idx}: {e}"
            )
            table_has_property = table_details.get("table_has_property", True)
            table_name = f"table_{idx}_page_{page_number}"

        box = {
            "table_name": table_name,
            "table_bounding_box": table_bounding_box,
            "page_number": page_number,
            "pdf_uuid": pdf_uuid,
            "page_id": page_id,
            "id": table_id,
            "columns": columns,
            "table_has_property": table_has_property,
            "parent_table_name": parent_table_name,
            "is_extracted": is_extracted,
            "is_validated": is_validated,
            "appearance_number": appearance_number,
        }
        input_table_data.append(box)
    logger.info(
        "DONE: Extracted bounding boxes from"
        f"document intelligence JSON data of page number {page_number}."
    )
    return input_table_data
