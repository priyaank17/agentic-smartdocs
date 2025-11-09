"""
This code sample shows Prebuilt Layout operations
with the Azure AI Document Intelligence client library."""

from io import BytesIO
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from src.utils.log import logger


# pylint: disable=no-name-in-module
def initialize_document_analysis_client(
    document_intelligence_endpoint, document_intelligence_api_key
):
    """
    Initialize the Azure Document Analysis Client.
    """
    if not document_intelligence_endpoint:
        raise ValueError("document_intelligence_endpoint cannot be empty")
    if not document_intelligence_api_key:
        raise ValueError("document_intelligence_api_key cannot be empty")
    return DocumentAnalysisClient(
        endpoint=document_intelligence_endpoint,
        credential=AzureKeyCredential(document_intelligence_api_key),
    )


def analyze_document(client, model_id, document_path):
    """
    Analyze a document using the specified model.
    """
    logger.info("INIT: Analyzing document")
    # with open(document_path, "rb") as document:
    #     poller = client.begin_analyze_document(model_id=model_id, document=document)
    #     result = poller.result()
    try:
        with open(document_path, "rb") as document:
            poller = client.begin_analyze_document(model_id=model_id, document=document)
            result = poller.result()
    except FileNotFoundError:
        logger.error(f"Document file not found: {document_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to analyze document {document_path}: {str(e)}")
        raise
    logger.info("DONE: Analyzed document")
    return result


def analyze_image(client, model_id, image_path):
    """
    Analyze an image using the specified model.
    """
    logger.info("INIT: Analyzing image")
    # Ensure the image file exists before attempting to open it
    try:
        with open(image_path, "rb") as image:
            poller = client.begin_analyze_document(model_id=model_id, document=image)
            result = poller.result()
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to analyze image {image_path}: {str(e)}")
        raise
    logger.info("DONE: Analyzed image")
    return result


def analyze_image_from_bytes(client, model_id, image_bytes):
    """
    Analyze an image from bytes using the specified model.
    """
    logger.info("INIT: Analyzing image from bytes")
    if not image_bytes:
        logger.error("No image bytes provided for analysis.")
        raise ValueError("Image bytes cannot be empty.")
    try:
        poller = client.begin_analyze_document(
            model_id=model_id, document=BytesIO(image_bytes)
        )
        result = poller.result()
    except Exception as e:
        logger.error(f"Failed to analyze image from bytes: {str(e)}")
        raise
    # poller = client.begin_analyze_document(
    #     model_id=model_id, document=BytesIO(image_bytes)
    # )
    # result = poller.result()
    logger.info("DONE: Analyzed image from bytes")
    return result
