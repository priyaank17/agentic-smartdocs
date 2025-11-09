"""LangGraph-based multi-agent orchestrator."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from langgraph.graph import END, StateGraph

from src.agents.classifier import DocumentClassifierAgent, DocumentClassification
# from src.agents.control_narrative import ControlNarrativeAgent
# from src.agents.process_narrative import ProcessNarrativeAgent
from src.agents.datasheet import DataSheetAgentPipeline
from src.config.settings import get_settings


@dataclass
class OrchestratorState:
    document_bytes: bytes
    payload: Dict[str, Any]
    temp_dir: Path
    classification: Optional[Dict[str, Any]] = None
    adm: Optional[Dict[str, Any]] = None
    logs: list[str] = field(default_factory=list)


class AgentOrchestrator:
    def __init__(self) -> None:
        self.classifier = DocumentClassifierAgent()
        # self.process_agent = ProcessNarrativeAgent()
        # self.control_agent = ControlNarrativeAgent()
        self.datasheet_pipeline = DataSheetAgentPipeline()
        self.graph = self._build_graph()
        self.settings = get_settings()

    def _build_graph(self):
        workflow = StateGraph(OrchestratorState)
        workflow.add_node("classify", self._classify_node)
        workflow.add_node("handle_narrative", self._handle_narrative_node)
        workflow.add_node("handle_datasheet", self._handle_datasheet_node)

        workflow.set_entry_point("classify")
        workflow.add_conditional_edges(
            "classify",
            self._route_classification,
            {
                "datasheet": "handle_datasheet",
                "process_narrative": "handle_narrative",
                "control_narrative": "handle_narrative",
            },
        )
        workflow.add_edge("handle_datasheet", END)
        workflow.add_edge("handle_narrative", END)
        return workflow.compile()

    def _route_classification(self, state: OrchestratorState) -> str:
        assert state.classification
        return state.classification.get("doc_type", "datasheet")

    async def _classify_node(self, state: OrchestratorState) -> OrchestratorState:
        if self.settings.skip_classifier:
            classification = DocumentClassification(doc_type="datasheet", confidence=1.0)
        else:
            classification = await self.classifier.classify(state.document_bytes)
        state.classification = classification.__dict__
        state.logs.append(f"classified as {classification.doc_type} ({classification.confidence:.2f})")
        return state

    async def _handle_narrative_node(self, state: OrchestratorState) -> OrchestratorState:
        assert state.classification
        doc_type = state.classification["doc_type"]
        if doc_type == "process_narrative":
            state.adm = await self.process_agent.extract(state.payload)
        else:
            state.adm = await self.control_agent.extract(state.payload)
        state.logs.append(f"ingested narrative for {doc_type}")
        return state

    async def _handle_datasheet_node(self, state: OrchestratorState) -> OrchestratorState:
        result = await self.datasheet_pipeline.run(
            document_bytes=state.document_bytes,
            workdir=state.temp_dir,
            asset_type=state.payload.get("asset_type", "generic"),
            database=state.payload.get("database"),
        )
        state.adm = result
        state.logs.append("datasheet ADM ingested")
        return state

    async def run(self, document_bytes: bytes, payload: Dict[str, Any], temp_dir: Path) -> Dict[str, Any]:
        initial_state = OrchestratorState(
            document_bytes=document_bytes,
            payload=payload,
            temp_dir=temp_dir,
        )
        final_state = await self.graph.ainvoke(initial_state)
        return {
            "classification": final_state.classification,
            "adm": final_state.adm,
            "logs": final_state.logs,
        }
