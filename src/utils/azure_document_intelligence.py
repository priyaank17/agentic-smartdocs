"""Helper for calling Azure Document Intelligence custom models."""

import base64
from typing import Any, Dict

import httpx

from src.config.settings import get_settings

settings = get_settings()


async def classify_document(document_bytes: bytes) -> Dict[str, Any]:
    """Invoke the Azure Document Intelligence endpoint for classification."""
    headers = {
        "Content-Type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": settings.azure_document_intelligence_key,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            settings.azure_document_intelligence_endpoint,
            headers=headers,
            content=document_bytes,
        )
        response.raise_for_status()
        return response.json()
