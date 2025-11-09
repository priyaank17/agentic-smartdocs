"""Graph ingestion agent for datasheet ADM."""

import json
from typing import Any, Dict, List

from src.utils.neo4j_client import ingest_adm

CATEGORIES = [
    "metadata",
    "equipments",
    "service_duty",
    "design_conditions",
    "operating_conditions",
    "fluid_data",
    "hydraulic_performance",
    "driver",
    "seal_system",
    "bearings_lubrication",
    "materials",
    "nozzles_connections",
    "nozzle_loads",
    "noise_vibration_limits",
    "instrumentation",
    "testing_inspection",
    "spare_parts",
    "baseplate_foundation",
    "accessories",
    "environmental_conditions",
    "weights",
    "auxiliary_utilities",
    "notes",
    "revisions",
    "centrifugal_specific",
    "vertical_turbine_specific",
    "reciprocating_specific",
    "rotary_specific",
    "submersible_specific",
]


def _serialize(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, ensure_ascii=False)


class GraphIngestionAgent:
    async def run(self, adm: Any, database: str | None = None) -> Dict[str, Any]:
        graph_payload = self._build_graph_payload(adm)
        return await ingest_adm(graph_payload, database)

    def _build_graph_payload(self, adm: Any) -> Dict[str, Any]:
        nodes: List[Dict[str, Any]] = []
        relationships: List[Dict[str, Any]] = []
        visited_ids = set()

        documents = adm if isinstance(adm, list) else [adm]
        for doc_index, doc in enumerate(documents):
            if not isinstance(doc, dict):
                continue
            metadata = doc.get("metadata") or {}
            asset_tag = (
                metadata.get("tag")
                or metadata.get("document_number")
                or metadata.get("equipment_name")
                or f"datasheet-{doc_index}"
            )
            asset_id = f"asset::{asset_tag}"
            if asset_id not in visited_ids:
                asset_node = {"id": asset_id, "label": "Asset", **metadata}
                nodes.append(asset_node)
                visited_ids.add(asset_id)

            equipments = doc.get("equipments") or [{}]
            for idx, equipment in enumerate(equipments):
                equipment = equipment or {}
                eq_name = equipment.get("equipment_name") or f"{asset_tag}-equipment-{idx}"
                eq_id = f"equipment::{eq_name}"
                if eq_id not in visited_ids:
                    eq_node = {"id": eq_id, "label": "Equipment", **equipment}
                    nodes.append(eq_node)
                    visited_ids.add(eq_id)
                relationships.append({"start": asset_id, "end": eq_id, "type": "HAS_EQUIPMENT"})

                for category in CATEGORIES:
                    data = equipment.get(category) if isinstance(equipment, dict) else None
                    if data is None:
                        data = doc.get(category)
                    if not data:
                        continue

                    category_id = f"{eq_id}::{category}"
                    if category_id not in visited_ids:
                        category_node = {
                            "id": category_id,
                            "label": "Category",
                            "category": category,
                            "data": _serialize(data),
                        }
                        nodes.append(category_node)
                        visited_ids.add(category_id)
                    relationships.append({"start": eq_id, "end": category_id, "type": "HAS_CATEGORY"})

                    if isinstance(data, dict):
                        for key, value in data.items():
                            detail_id = f"{category_id}::{key}"
                            if detail_id in visited_ids:
                                continue
                            detail_node = {
                                "id": detail_id,
                                "label": "Detail",
                                "key": key,
                                "value": _serialize(value),
                            }
                            nodes.append(detail_node)
                            visited_ids.add(detail_id)
                            relationships.append({"start": category_id, "end": detail_id, "type": "HAS_DETAIL"})
                    elif isinstance(data, list):
                        for list_idx, entry in enumerate(data):
                            entry_id = f"{category_id}::item-{list_idx}"
                            if entry_id in visited_ids:
                                continue
                            entry_node = {
                                "id": entry_id,
                                "label": "Entry",
                                "data": _serialize(entry),
                            }
                            nodes.append(entry_node)
                            visited_ids.add(entry_id)
                            relationships.append({"start": category_id, "end": entry_id, "type": "HAS_ENTRY"})

        return {"nodes": nodes, "relationships": relationships}
