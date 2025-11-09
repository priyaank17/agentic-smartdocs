# SmartDocs Agentic Platform

This repository refactors the original SmartDocs Lambda project into a fully agentic, multi-tenant document-analysis platform. It introduces a LangGraph-based orchestrator, multi-agent datasheet pipelines, Azure Document Intelligence classification, Paligemma inference on vLLM, and production-grade deployment assets for Azure AKS/ACR.

## High-Level Architecture

- **Shared Legacy Logic** – preserved under `src/core`, a direct copy of the Lambda-era codebase.
- **Agents** – `src/agents` contains classifier, narrative (process/control), and the six-stage datasheet pipeline (splitter, vision, validation, schema compliance, aggregator, graph ingestion).
- **Orchestrator** – `src/orchestrator/langgraph_flow.py` wires agents with LangGraph, enabling planning, routing, and retry semantics.
- **Inference** – `src/inference` hosts the Paligemma + vLLM server for multi-modal extraction.
- **FastAPI** – `src/api/main.py` exposes `/classify_doc`, `/process_narrative`, `/control_narrative`, `/datasheet`, `/ingest_to_graph`, `/orchestrate`, and `/health`.
- **Deployments** – `src/deployments` provides Dockerfiles, AKS manifests (with GPU node-pool support), Helm chart, and ACR push script.

## Getting Started

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8080
```

To run the LangGraph orchestrator end-to-end:

```bash
curl -X POST "http://localhost:8080/orchestrate" \
     -F "file=@sample.pdf" \
     -F 'payload={"plant_id":"XYZ","asset_type":"pump"}'
```

The vLLM inference server can be launched with:

```bash
uvicorn src.inference.vllm_server:app --host 0.0.0.0 --port 9000
```

## AKS Deployment

1. Build and push images to ACR using `src/deployments/acr/push.sh`.
2. Apply `src/deployments/aks/*.yaml` to provision namespace, secrets, API deployment, GPU-backed vLLM deployment, and HPAs.
3. Optionally install via Helm: `helm install smartdocs ./src/deployments/helm`.

## Environment Variables

- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `PALIGEMMA_MODEL_NAME`, `PALIGEMMA_LORA_PATH` (optional)
- `VLLM_HOST`, `VLLM_PORT`
- `VA_API_KEY` (Landing AI Agentic Document Analysis key)

See `src/config/settings.py` for the full list.

## CI/CD

GitHub Actions ( `.github/workflows/ci.yaml`) runs lint, unit tests, and Docker builds for each service image, ready to wire to environment-specific deployments.
