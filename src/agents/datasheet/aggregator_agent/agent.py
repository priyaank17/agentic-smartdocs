"""Aggregates page-level JSON into a consolidated ADM."""

from typing import Any, Dict, List


class AggregatorAgent:
    async def run(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        adm = {"nodes": [], "relationships": []}
        for idx, page in enumerate(pages):
            page = page or {}
            node_id = (
                page.get("id")
                or page.get("equipment", {}).get("equipment_name")
                or f"datasheet-node-{idx}"
            )
            node = dict(page)
            node["id"] = node_id
            adm["nodes"].append(node)
        return adm
