"""
This code sample shows Prebuilt Layout operations with the
Azure AI Document Intelligence client library.
"""

import os

# import json
from src.utils.log import logger
from src.utils.document_analysis_utils import (
    initialize_document_analysis_client,
    analyze_document,
    analyze_image,
    analyze_image_from_bytes,
)
from src.utils.s3_download_upload import save_json_to_storage, check_file_in_storage


def load_azure_document_intelligence_credentials():
    """
    Load Azure Document Intelligence credentials from environment variables.
    """
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    api_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_KEY")

    if not endpoint or not api_key:
        raise EnvironmentError(
            "Azure Document Intelligence endpoint and API key "
            "must be set in environment variables."
        )

    return endpoint, api_key


def extract_data_document_intelligence(
    path_or_bytes, file_type, model_id="prebuilt-layout"
):
    """
    This function uses the Azure AI Document Intelligence client library
    to analyze a given document using the prebuilt layout model.
    """
    document_intelligence_endpoint, document_intelligence_api_key = (
        load_azure_document_intelligence_credentials()
    )

    client = initialize_document_analysis_client(
        document_intelligence_endpoint, document_intelligence_api_key
    )
    if file_type == "pdf":
        result = analyze_document(
            client, model_id=model_id, document_path=path_or_bytes
        )
    elif file_type == "image":
        result = analyze_image(client, model_id=model_id, image_path=path_or_bytes)
    elif file_type == "image_bytes":
        result = analyze_image_from_bytes(client, model_id, image_bytes=path_or_bytes)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    logger.info("Document intelligence extraction completed successfully.")
    return result


def custom_serializer(obj):
    """
    Custom serializer for JSON serialization.
    """
    if isinstance(obj, dict):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def remove_spans(json_data):
    """Remove the 'spans' key from the 'lines' in the JSON data."""
    for page in json_data["analyzeResult"]["pages"]:
        for line in page["lines"]:
            if "spans" in line:
                del line["spans"]  # Remove the 'spans' key
    return json_data


async def get_document_intelligence(
    bucket_name,
    path,
    extracted_document_intelligence_output_path,
    file_type,
):
    """Extract document intelligence from a given document."""
    logger.info("INIT: Extracting document intelligence.")
    if not await check_file_in_storage(
        bucket_name, extracted_document_intelligence_output_path
    ):
        logger.info("File does not exist, extracting using document intelligence.")
        try:
            raw_document_intelligence_output = extract_data_document_intelligence(
                path, file_type, model_id="prebuilt-layout"
            )
        except Exception as e:
            logger.error(f"Failed to extract document intelligence: {e}")
            raise
        logger.info("Document intelligence extraction completed successfully.")
        logger.info("INIT: Filtering document intelligence data and saving to storage.")
        try:
            filtered_document_intelligence_output_dict = (
                raw_document_intelligence_output.to_dict()
            )
            document_intelligence_json_data = {
                "analyzeResult": filtered_document_intelligence_output_dict
            }
            await save_json_to_storage(
                bucket_name,
                extracted_document_intelligence_output_path,
                document_intelligence_json_data,
            )
        except Exception as e:
            logger.error(f"Failed to save document intelligence data: {e}")
            raise
        logger.info(
            f"""DONE: Document intelligence extracted and
            saved to {extracted_document_intelligence_output_path}"""
        )

    else:
        logger.info(
            f"Output file already exists: {extracted_document_intelligence_output_path}"
        )


def filter_document_intelligence_data(
    extracted_document_intelligence_json_data, page_number
):
    """Filter document intelligence data."""
    filter_data = remove_spans(extracted_document_intelligence_json_data)
    if "analyzeResult" not in filter_data:
        raise ValueError("Invalid document intelligence data format.")
    if "pages" not in filter_data["analyzeResult"]:
        raise ValueError("No pages found in the document intelligence data.")
    if not filter_data["analyzeResult"]["pages"]:
        raise ValueError("No pages found in the document intelligence data.")
    page_index = page_number - 1
    if page_index < 0 or page_index >= len(filter_data["analyzeResult"]["pages"]):
        raise ValueError(f"Page number {page_number} is out of range for the document.")
    if "lines" not in filter_data["analyzeResult"]["pages"][page_index]:
        raise ValueError(f"No lines found on page {page_number} in the document.")
    return filter_data["analyzeResult"]["pages"][page_index]["lines"]
