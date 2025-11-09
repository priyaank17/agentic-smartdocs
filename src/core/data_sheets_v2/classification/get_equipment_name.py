"""Script to classify a PDF document using Azure Document Intelligence."""

import os
from io import BytesIO
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from src.utils.log import logger
from src.utils.s3_download_upload import load_into_memory


async def classify_pdf_document(bucket, endpoint, key, model_id, pdf_path):
    """
    Classifies a PDF document using Azure Document Intelligence.
    """
    logger.info("INIT: classify_pdf_document")
    print(pdf_path)
    client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    pdf_bytes = await load_into_memory(bucket, pdf_path)

    client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    poller = client.begin_classify_document(
        classifier_id=model_id, body=BytesIO(pdf_bytes)
    )
    result = poller.result()

    document_type = result.documents[0].get("docType")
    if document_type:
        logger.info(f"DONE: Document type: {document_type}")
        return document_type

    logger.warning("Document type not found.")
    return None


async def get_asset_type(bucket, pdf_path):
    """
    Maps the classified document type to a specific asset type.
    """
    logger.info("INIT: get_asset_type")
    document_intelligence_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    document_intelligence_api_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_KEY")
    classification_model_name = os.getenv(
        "AZURE_DOCUMENT_INTELLIGENCE_CLASSIFICATION_MODEL_NAME"
    )

    # Ensure required values are present
    if not all(
        [
            document_intelligence_endpoint,
            document_intelligence_api_key,
            classification_model_name,
        ]
    ):
        raise EnvironmentError(
            "One or more Azure Document Intelligence environment variables are missing."
        )

    # Classify document using Azure Document Intelligence
    classified_equipment_type = await classify_pdf_document(
        bucket,
        document_intelligence_endpoint,
        document_intelligence_api_key,
        classification_model_name,
        pdf_path,
    )
    mapping = {
        "drum_pressure_vessel_data_sheet": "drum",
        "heat_exchanger_air_cooler_data_sheet": "heat_exchanger_air_cooled",
        "heat_exchanger_other_data_sheet": "heat_exchanger_other",
        "heat_exchanger_shell_and_tube_data_sheet": "heat_exchanger_shell_and_tube",
        "pump_data_sheet": "pump",
    }
    return mapping.get(classified_equipment_type, "unknown")
