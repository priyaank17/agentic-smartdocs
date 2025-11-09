"""PDF utilities used by datasheet agents."""

from pathlib import Path
from typing import List

import fitz  # pymupdf


def pdf_to_images(pdf_bytes: bytes, output_dir: Path) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    image_paths = []
    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image_path = output_dir / f"page-{page_index+1}.png"
        pix.pil_save(image_path)
        image_paths.append(image_path)
    return image_paths
