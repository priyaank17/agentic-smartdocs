import json
from pathlib import Path
from typing import Any, Dict

from .vision_agent.agent import VisionExtractionAgent
from .validation_agent.agent import ValidationAgent
from .schema_agent.agent import SchemaComplianceAgent
from .aggregator_agent.agent import AggregatorAgent
from .graph_agent.agent import GraphIngestionAgent


class DataSheetAgentPipeline:
    def __init__(self) -> None:
        self.vision = VisionExtractionAgent()
        self.validator = ValidationAgent()
        # self.schema = SchemaComplianceAgent()
        # self.aggregator = AggregatorAgent()
        self.graph = GraphIngestionAgent()

    async def run(self, document_bytes: bytes, workdir: Path, asset_type: str, database: str | None = None) -> Dict[str, Any]:
        pdf_path = workdir / "input.pdf"
        pdf_path.write_bytes(document_bytes)

        outputs_dir = Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        base_name = pdf_path.stem

        pages = await self.vision.run(pdf_path, asset_type)
        (outputs_dir / f"{base_name}_vision.json").write_text(json.dumps(pages, indent=2, ensure_ascii=False))

        validated = await self.validator.run(pages)
        (outputs_dir / f"{base_name}_validated.json").write_text(json.dumps(validated, indent=2, ensure_ascii=False))

        # schema_aligned = await self.schema.run(asset_type, validated)
        # (outputs_dir / f"{base_name}_schema.json").write_text(json.dumps(schema_aligned, indent=2, ensure_ascii=False))

        # adm = await self.aggregator.run(schema_aligned)
        # (outputs_dir / f"{base_name}_adm.json").write_text(json.dumps(adm, indent=2, ensure_ascii=False))

        graph_result = await self.graph.run(validated, database)
        return {"adm": validated, "graph": graph_result}
