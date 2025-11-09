"""Process narrative pipeline agent."""

from typing import Any, Dict

from src.core.events import handle_EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA
from src.core.events import handle_TRIGGERED_PROCESS_NARRATIVE_RAG_JUNIOR_DATA_ACTION
from src.utils.neo4j_client import ingest_adm


class ProcessNarrativeAgent:
    async def extract(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the existing RAG Junior extraction pipeline."""
        result = await handle_EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA(payload)
        adm = payload.get("adm")
        if adm:
            graph_result = await ingest_adm(adm, payload.get("database"))
            result["graph"] = graph_result
        return result

    async def trigger_background(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await handle_TRIGGERED_PROCESS_NARRATIVE_RAG_JUNIOR_DATA_ACTION(payload)
