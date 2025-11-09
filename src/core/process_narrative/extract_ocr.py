"""Extract OCR data from a JSON file."""

import pandas as pd
from src.utils.s3_download_upload import load_json_from_storage, save_df_to_storage
from src.utils.invoke_ocr_lambda import get_ocr_file
from src.utils.log import logger


async def _generate_and_save_ocr_file(bucket, input_path):
    """Save OCR extracted data."""
    data = await load_json_from_storage(bucket, input_path)

    for table_data in data["tables_data"]:
        page_id = table_data.get("page_id")
        image_path = input_path.replace("input_data.json", f"{page_id}")
        ocr_output_json_path = input_path.replace("input_data.json", f"{page_id}.json")
        await get_ocr_file(bucket, image_path, ocr_output_json_path)


async def _get_bounding_box_data(bucket, input_path):
    """Get bounding box data."""
    data = await load_json_from_storage(bucket, input_path)
    all_filtered_data = {}
    for table_data in data["tables_data"]:
        narrative_id = table_data.get("narrative_id")
        page_id = table_data.get("page_id")
        table_bounding_box = table_data.get("table_bounding_box")
        ocr_output_json_path = input_path.replace("input_data.json", f"{page_id}.json")
        ocr_data = await load_json_from_storage(bucket, ocr_output_json_path)
        filtered_data = extract_bounding_box(ocr_data, page_id, table_bounding_box)
        if narrative_id in all_filtered_data:
            all_filtered_data[narrative_id] += "\n" + filtered_data
        else:
            all_filtered_data[narrative_id] = filtered_data
    df_filtered_data = pd.DataFrame(list(all_filtered_data.items()), columns=['id', 'text'])
    return df_filtered_data


def extract_bounding_box(data, page_id, bounding_box):
    """Extract text within a bounding box."""
    text_within_bounding_box = ""
    del data[next(iter(data))]["text_annotations"][0]
    annotations = data[f"{page_id}"]["text_annotations"]
    for annotation in annotations:
        vertices = annotation["bounding_poly"]["vertices"]
        if is_within_bounding_box(vertices, bounding_box):
            text_within_bounding_box = text_within_bounding_box + " " + annotation["description"]
    return text_within_bounding_box


def is_within_bounding_box(vertices, bounding_box):
    """Check if a list of vertices is within a bounding box."""
    for vertex in vertices:
        x, y = vertex["x"], vertex["y"]
        if not (
            bounding_box["x_min"] <= x <= bounding_box["x_max"]
            and bounding_box["y_min"] <= y <= bounding_box["y_max"]
        ):
            return False
    return True


async def create_narrative_csv(bucket, input_data_path):
    """Create a CSV file having control narrative data within bounding box."""
    logger.info("Extracting OCR data and creating CSV file")
    await _generate_and_save_ocr_file(bucket, input_data_path)
    ocr_filtered_df = await _get_bounding_box_data(bucket, input_data_path)
    csv_path = input_data_path.replace("input_data.json", "narrative_paragraphs.csv")
    await save_df_to_storage(bucket, csv_path, ocr_filtered_df)
    logger.info("CSV file created and saved successfully")
