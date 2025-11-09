# Pipelines

## Narrative RAG
- Classification routes to process vs control agents.
- Agents call legacy handlers in `src.core.events` and output ADM JSON.
- ADM is ingested through `src/utils/neo4j_client.py` ensuring Neo4j access via env vars.

## Datasheet Multi-Agent Flow
1. **PDF Splitter** – converts PDF to per-page PNG using PyMuPDF.
2. **Vision Extraction** – sends images to Paligemma on vLLM for structured JSON.
3. **Validation** – checks for missing fields and types.
4. **Schema Compliance** – matches JSON with reference DEXPI/ADM schema.
5. **Aggregator** – merges page-level data to a global ADM.
6. **Graph Ingestion** – pushes ADM into Neo4j with unified interface.

## Orchestrator
- Implemented with LangGraph providing retry/state handling.
- Input: PDF bytes + metadata.
- Output: ADM payload + Neo4j ingestion logs + classification summary.
