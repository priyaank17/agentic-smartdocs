"""Splits PDFs into page-level PNGs."""

from pathlib import Path
from typing import List

from src.utils.pdf import pdf_to_images


class PdfSplitterAgent:
    async def run(self, document_bytes: bytes, workdir: Path) -> List[Path]:
        return pdf_to_images(document_bytes, workdir)
