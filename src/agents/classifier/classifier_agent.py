"""Agent that classifies incoming PDFs using Azure Document Intelligence."""

from dataclasses import dataclass
from typing import Literal

from src.utils.azure_document_intelligence import classify_document


@dataclass
class DocumentClassification:
    doc_type: Literal["process_narrative", "control_narrative", "datasheet"]
    confidence: float


class DocumentClassifierAgent:
    async def classify(self, document_bytes: bytes) -> DocumentClassification:
        response = await classify_document(document_bytes)
        prediction = response.get("prediction", {})
        doc_type = prediction.get("label", "datasheet")
        confidence = float(prediction.get("confidence", 0.5))
        if doc_type not in {"process_narrative", "control_narrative", "datasheet"}:
            doc_type = "datasheet"
        return DocumentClassification(doc_type=doc_type, confidence=confidence)
