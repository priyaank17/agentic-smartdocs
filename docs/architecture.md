# Agentic Architecture

1. **Classification Layer** – `DocumentClassifierAgent` calls Azure Document Intelligence to determine whether the PDF is a process narrative, control narrative, or datasheet. Output format: `{ "doc_type": ..., "confidence": ... }`.
2. **Narrative Pipelines** – `ProcessNarrativeAgent` and `ControlNarrativeAgent` reuse the original RAG Junior flows inside `src/core` and normalize ADM output before ingestion.
3. **Datasheet Multi-Agent System** – The six agents under `src/agents/datasheet` orchestrate splitting, Paligemma VLM inference via vLLM, validation, schema alignment, aggregation, and graph ingestion.
4. **Orchestrator** – `langgraph_flow.py` models the workflow as a LangGraph with branching on the classifier output, allowing retries, state management, and composable planning.
5. **Inference** – `src/inference/vllm_server.py` runs Paligemma with vLLM on a GPU node pool. The datasheet vision agent interacts with `/vision/completions`.
6. **Deployment** – Dockerfiles and AKS manifests provide FastAPI + vLLM services, HPAs, GPU scheduling, and ACR integration.
