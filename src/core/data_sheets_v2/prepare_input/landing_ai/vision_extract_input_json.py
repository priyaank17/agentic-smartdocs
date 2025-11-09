"""
This module processes images from a specified S3 bucket, extracts grounding data and bounding boxes,
and saves the results as JSON entries. It uses the `agentic_doc` library for parsing
and the `PIL` library for image handling.
"""

import re
import uuid
from io import BytesIO
from PIL import Image
from agentic_doc.parse import parse  # type: ignore
from agentic_doc.common import ChunkType  # type: ignore
from src.utils.s3_download_upload import load_into_memory
from src.data_sheets_v2.prepare_input.bounding_box.extract_table_has_property_info import (
    get_table_info_llm,
)


async def parse_pages(bucket_name: str, image_path_list: list) -> list:
    """
    Parses page images, extracts grounding data and bounding boxes, and saves them as JSON.
    """
    input_data_entries = []
    table_idx = 1
    figure_idx = 1
    for image_path in image_path_list:
        try:
            file_bytes = await load_into_memory(bucket_name, image_path)
            if not file_bytes:
                print(f"[ERROR] No data found for image: {image_path}")
                continue

            parsed_docs = parse(file_bytes)
            image = Image.open(BytesIO(file_bytes))
            width, height = image.size
            image_info = str(image_path).split("+")
            doc = parsed_docs[0]  # Assuming single document per image

            for chunk in doc.chunks:
                table_type = chunk.chunk_type.value
                if table_type == "marginalia":
                    continue
                for g in chunk.grounding:
                    table_bounding_box = {
                        "x_min": g.box.l * width,
                        "x_max": g.box.r * width,
                        "y_min": g.box.t * height,
                        "y_max": g.box.b * height,
                    }
                    page_number = int(image_info[-1])
                    table_has_property = True
                    table_name = ""
                    table_info_llm = await get_table_info_llm(
                        bucket_name, image_path, table_bounding_box
                    )
                    table_has_property = table_info_llm[0].get(
                        "table_has_property", True
                    )
                    table_name = table_info_llm[0].get("table_name")
                    # if table_type != "figure":
                    #     table_info_llm = await get_table_info_llm(
                    #         bucket_name, image_path, table_bounding_box
                    #     )
                    #     table_has_property = table_info_llm[0].get(
                    #         "table_has_property", True
                    #     )
                    #     table_name = table_info_llm[0].get("table_name")
                    # else:
                    #     table_has_property = False
                    #     table_name = f"figure_{figure_idx}_page_{page_number}"
                    #     figure_idx += 1

                    if not table_name:
                        if table_type == "figure":
                            table_name = f"figure_{figure_idx}_page_{page_number}"
                            figure_idx += 1
                        else:
                            table_name = f"table_{table_idx}_page_{page_number}"
                            table_idx += 1
                    else:
                        table_name = table_name.strip().replace(" ", "_").lower()
                        table_name = re.sub(r"[^a-zA-Z0-9_]", "", table_name)

                    # last_part = image_path.split("/")[-1]
                    image_id = image_info[0].split("/")[-1]
                    page_id = image_path.split("/")[-1]

                    entry = {
                        "table_name": table_name,
                        "table_bounding_box": table_bounding_box,
                        "parent_table_name": "",
                        "page_number": page_number,
                        "pdf_uuid": image_id,
                        "page_id": page_id,
                        "id": str(uuid.uuid4()),
                        "columns": [],
                        "table_has_property": table_has_property,
                        "type": table_type,
                        "is_extracted": False,
                        "appearance_number": 1,
                        "is_validated": False,
                        "markdown": (
                            chunk.text
                            if chunk.chunk_type in {ChunkType.text, ChunkType.figure}
                            else None
                        ),
                        # "snippet_image": (
                        #     str(g.image_path)
                        #     if chunk.chunk_type == ChunkType.table and g.image_path
                        #     else None
                        # ),
                        # "chunk_index": idx,
                    }
                    input_data_entries.append(entry)
        except (IOError, ValueError, AttributeError) as e:
            print(f"[ERROR] Parsing document {e}")

    return input_data_entries
