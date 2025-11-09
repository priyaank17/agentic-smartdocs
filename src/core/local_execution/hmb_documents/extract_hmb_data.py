"""This module contains functions to extract data from HMB documents."""

import io
import pdfplumber
import pandas as pd
from src.utils.log import logger
from src.local_execution.hmb_documents.post_process_hmb_data import process_hmb_data
from src.utils.storage_utils import (
    fetch_file_via_adapter,
    fetch_cloud_pdf_via_adapter,
    upload_file_to_storage,
)


async def extract_tables_from_pdf(
    bucket_name, pdf_file_path, table_json_path, output_directory, output_json_path
):
    """
    Extracts tables from a PDF document and saves them as CSV files.

    Args:
        pdf_path (str): The path to the PDF document.
        json_path (str): The path to the JSON file containing table data.
        output_directory (str): The directory where the CSV files will be saved.

    Returns:
        None

    Raises:
        FileNotFoundError: If the PDF file or the JSON file does not exist.

    Prints:
        Information about the extracted tables and the process of saving them to CSV files.

    """
    table_data = await load_table_data(bucket_name, table_json_path)
    await process_tables(bucket_name, pdf_file_path, table_data, output_directory)
    await process_hmb_data(
        folder_path=output_directory,
        bucket=bucket_name,
        output_json_path=output_json_path,
        metadata_file=table_json_path,
    )


async def load_table_data(bucket_name, file_name):
    """
    Load table data from a JSON file.

    Args:
        json_path (str): The path to the JSON file.

    Returns:
        List[Dict[str, str]]: A list of dictionaries representing the table data.
          Each dictionary contains the
        table data with keys as the column names and values as the corresponding cell values.
    """
    logger.info("Loading table data")
    data = await fetch_file_via_adapter(bucket_name, file_name)
    table_data = data["tables_data"]
    table_data = sorted(
        table_data,
        key=lambda x: (
            x["page_number"],
            x["table_number"],
            x["table_type"] == "sub_part",
        ),
    )
    return table_data


async def process_tables(bucket_name, pdf_file_path, table_data, output_directory):
    """
    Process tables from a PDF document and save them as CSV files.

    Args:
        pdf_path (str): The path to the PDF document.
        table_data (List[Dict[str, str]]): A list of dictionaries containing table data.
        Each dictionary has the following keys:
           * - page_number (str): The page number of the table.
            - table_number (str): The table number.
            - bounding_box (str): The bounding box of the table.
            - table_type (str): The type of the table.
            - table_title (str): The title of the table.
            - table_uuid (str): The UUID of the table.
        output_directory (str): The directory where the CSV files will be saved.

    Returns:
        Tuple[Dict[str, pd.DataFrame], List[str]]:
        A tuple containing two elements:
            - headings (Dict[str, pd.DataFrame]):
            A dictionary mapping table UUIDs to their corresponding DataFrames.
            - bounding_box_info (List[str]):
            A list of strings representing bounding box information.

    Raises:
        FileNotFoundError: If the PDF file does not exist.

    Prints:
        Information about the extracted tables and the process of saving them to CSV files.

    """
    response = await fetch_cloud_pdf_via_adapter(bucket_name, pdf_file_path)

    file_bytes = response.data.data
    headings = {}
    bounding_box_info = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for entry in table_data:
            safe_table_title = clean_table_title(entry["table_title"])
            safe_table_title = safe_table_title.lower()
            if int(entry["page_number"]) - 1 < len(pdf.pages):
                page = pdf.pages[int(entry["page_number"]) - 1]
                page_width_points = page.width
                page_height_points = page.height
                image_width_pixels = 6525
                image_height_pixels = 4275
                # Calculate scaling factors
                scale = [page_width_points / image_width_pixels,
                         page_height_points / image_height_pixels]
                bounding_box = [
                    entry["table_bounding_box"]["x_min"] * scale[0],
                    entry["table_bounding_box"]["y_min"] * scale[1],
                    entry["table_bounding_box"]["x_max"] * scale[0],
                    entry["table_bounding_box"]["y_max"] * scale[1],
                ]
                cropped_page = page.crop(bounding_box)
                table = cropped_page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df = df.fillna("")
                    if entry["table_type"] == "heading":
                        headings[entry["table_uuid"]] = df
                        # print(df)
                    elif entry["table_type"] == "sub_part" and entry["table_uuid"] in headings:
                        subpart_df = pd.DataFrame(
                            table, columns=headings[entry["table_uuid"]].columns
                        )
                        df = df.fillna("")
                        subpart_df = subpart_df.fillna("")
                        combined_df = pd.concat(
                            [headings[entry["table_uuid"]], subpart_df],
                            axis=0,
                            ignore_index=True,
                        )
                        csv_filename = (
                            "page" + str(int(entry["page_number"])) + "_"
                            "table" + str(int(entry["table_number"])) + "_"
                            + safe_table_title + ".csv"
                        )

                        csv_buffer = io.BytesIO()
                        combined_df.to_csv(csv_buffer, index=False, encoding="utf-8")
                        csv_buffer.seek(0)
                        await upload_file_to_storage(
                            bucket_name,
                            f"{output_directory}/{csv_filename}",
                            csv_buffer,
                        )
                        logger.info(
                            f"saved in the path: {output_directory}/{csv_filename}"
                        )
                    # else:
                    #     csv_filename = f"page{page_number}_
                    # table{table_number}_{safe_table_title}.csv"
                    #     csv_buffer = io.BytesIO()
                    #     combined_df.to_csv(csv_buffer, index=False, encoding='utf-8')
                    #     csv_buffer.seek(0)
                    #     s3.upload_fileobj(csv_buffer, bucket_name,
                    # f'{output_directory}/{csv_filename}')
                    #     logger.info(f"saved in the path: {output_directory}/{csv_filename}")
                    logger.info(
                        "Saved Page " + str(int(entry["page_number"])) + " - "
                        "Table " + str(int(entry["table_number"])) + " as "
                        + entry["table_type"] + ": "
                        + entry["table_title"]
                    )
                    bounding_box_info = extract_bounding_box_info(
                        cropped_page, table, bounding_box_info, int(
                            entry["table_number"])
                    )
                else:
                    logger.info(
                        f"""No table found on page {int(entry["page_number"])} with bounding box {
                            bounding_box}"""
                    )
    return headings, bounding_box_info


def clean_table_title(table_title):
    """
    Cleans the given table title by replacing any non-alphanumeric characters with underscores.

    Parameters:
        table_title (str): The table title to be cleaned.

    Returns:
        str: The cleaned table title.
    """
    return "".join([c if c.isalnum() or c in (" ", "_") else "_" for c in table_title])


def extract_bounding_box_info(cropped_page, table, bounding_box_info, table_number):
    """
    Extracts bounding box information for each cell in a given table.

    Parameters:
        cropped_page (pdfplumber.page.Page): The cropped page object from which to extract words.
        table (List[List[str]]): The table for which to extract bounding box information.
        bounding_box_info (List[str]): The list to store bounding box information.
        table_number (int): The number of the table.

    Returns:
        List[str]: The updated list of bounding box information.
    """
    bounding_box_info.append(f"Bounding box information for Table {table_number}:")
    for row in table[1:]:
        for cell in row:
            if cell is not None:
                words = cropped_page.extract_words(
                    use_text_flow=True, keep_blank_chars=True
                )
                for word in words:
                    if word["text"] == cell:
                        bbox_info = (
                            f"{cell}: x0={word['x0']}, "
                            f"top={word['top']}, "
                            f"x1={word['x1']}, "
                            f"bottom={word['bottom']}"
                        )
                        bounding_box_info.append(bbox_info)
    bounding_box_info.append("")
    return bounding_box_info


if __name__ == "__main__":
    extract_tables_from_pdf(
        bucket_name="",
        pdf_file_path="",
        table_json_path="",
        output_directory="",
        output_json_path="",
    )
