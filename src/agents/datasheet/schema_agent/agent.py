"""Schema compliance agent that aligns JSON with ADM/DEXPI schema."""

from pathlib import Path
from typing import Any, Dict, List

import json

SCHEMA_DIR = Path(__file__).resolve().parents[4] / "data" / "schemas"

FALLBACK_FIELDS = ["asset_name", "service", "operating_conditions"]


class SchemaComplianceAgent:
    def __init__(self) -> None:
        self.cache: Dict[str, List[str]] = {}

    def _load_fields(self, asset_type: str) -> List[str]:
        if asset_type in self.cache:
            return self.cache[asset_type]
        schema_file = SCHEMA_DIR / f"{asset_type}_schema.json"
        if not schema_file.exists():
            schema_file = SCHEMA_DIR / "datasheet.adm.schema.json"
        if schema_file.exists():
            schema = json.loads(schema_file.read_text(encoding="utf-8"))
            fields = [field["name"] for field in schema.get("fields", [])]
        else:
            fields = FALLBACK_FIELDS
        self.cache[asset_type] = fields
        return fields

    async def run(self, asset_type: str, page_jsons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        fields = self._load_fields(asset_type)
        aligned_pages = []
        for page in page_jsons:
            aligned = {field: page.get(field) for field in fields}
            aligned_pages.append(aligned)
        return aligned_pages
