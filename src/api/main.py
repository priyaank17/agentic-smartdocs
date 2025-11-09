"""FastAPI surface for the SmartDocs agentic system."""

import tempfile
from pathlib import Path
from typing import Any, Dict

import json
from fastapi import Body, FastAPI, File, UploadFile, HTTPException

from src.agents.classifier import DocumentClassifierAgent
# from src.agents.process_narrative import ProcessNarrativeAgent
# from src.agents.control_narrative import ControlNarrativeAgent
from src.agents.datasheet import DataSheetAgentPipeline
from src.agents.datasheet.graph_agent.agent import GraphIngestionAgent
from src.orchestrator.langgraph_flow import AgentOrchestrator

app = FastAPI(title="SmartDocs Agentic Platform")

classifier_agent = DocumentClassifierAgent()
# process_agent = ProcessNarrativeAgent()
# control_agent = ControlNarrativeAgent()
Datasheet_pipeline = DataSheetAgentPipeline()
graph_agent = GraphIngestionAgent()
orchestrator = AgentOrchestrator()
DEFAULT_PAYLOAD = {
    "plant_id": "UNKNOWN",
    "asset_type": "pumps",
    "database": "neo4j",
}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/classify_doc")
async def classify_doc(file: UploadFile = File(...)):
    document_bytes = await file.read()
    classification = await classifier_agent.classify(document_bytes)
    return classification.__dict__


# @app.post("/process_narrative")
# async def process_narrative(payload: Dict[str, Any] = Body(...)):
#     return await process_agent.extract(payload)


# @app.post("/control_narrative")
# async def control_narrative(payload: Dict[str, Any] = Body(...)):
#     return await control_agent.extract(payload)


@app.post("/datasheet")
async def datasheet(
    file: UploadFile = File(...), asset_type: str = "generic", database: str | None = None
):
    document_bytes = await file.read()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await Datasheet_pipeline.run(
            document_bytes=document_bytes,
            workdir=Path(tmpdir),
            asset_type=asset_type,
            database=database,
        )
    return result


@app.post("/ingest_to_graph")
async def ingest_to_graph(adm: Any = Body(...), database: str | None = None):
    return await graph_agent.run(adm, database)


def _ensure_dict(payload: Dict[str, Any] | str | None) -> Dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, dict):
        return payload
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="payload must be valid JSON") from exc


@app.post("/orchestrate")
async def orchestrate(
    file: UploadFile = File(...), payload: Dict[str, Any] | str | None = Body(default=None)
):
    document_bytes = await file.read()
    payload = _ensure_dict(payload)
    if not payload:
        payload = DEFAULT_PAYLOAD.copy()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await orchestrator.run(document_bytes, payload, Path(tmpdir))
    return result
