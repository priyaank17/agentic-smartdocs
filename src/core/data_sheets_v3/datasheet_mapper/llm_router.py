"""
datasheet_mapper.llm_router
LangChain wrapper around Azure OpenAI + a cached alias-matching helper.
"""

from __future__ import annotations

import os
import json
import functools
from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage

# ── 1. read the required env-vars ─────────────────────────────────────────
AZ_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")  # e.g. 'abc123…'
AZ_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT"
)  # 'https://<resource>.openai.azure.com/'
AZ_DEPLOY = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"
)  # 'gpt-4o' (deployment name, *not* model)
AZ_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")  # default if unset

if not all((AZ_API_KEY, AZ_ENDPOINT, AZ_DEPLOY)):
    raise EnvironmentError(
        "Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, "
        "and AZURE_OPENAI_DEPLOYMENT_NAME before importing llm_router."
    )

# ── 2. create one shared LangChain LLM object ─────────────────────────────
LLM = AzureChatOpenAI(
    azure_endpoint=AZ_ENDPOINT,
    deployment_name=AZ_DEPLOY,
    api_key=AZ_API_KEY,
    api_version=AZ_VERSION,
    temperature=0,
)


# ── 3. cached helper for entity / property mapping ────────────────────────
@functools.lru_cache(maxsize=128)
def llm_match(question: str) -> dict[str, str]:
    """
    Ask LLM to map a raw string to the canonical schema.
    Returns {} on parse error.
    """
    system_prompt = (
        "You map raw datasheet strings to canonical schema keys.\n"
        "Examples:\n"
        'TABLE: "PROCESS NOZZLES"  →  {"entity":"process_nozzles"}\n'
        'TABLE: "MECHANICAL  DATA" →  {"entity":"mechanical_geometry"}\n'
        "Respond ONLY with JSON containing entity or property."
    )
    messages = [
        SystemMessage(content=system_prompt),
        {"role": "user", "content": question},
    ]

    resp = LLM.invoke(messages, response_format={"type": "json_object"})
    try:
        return json.loads(resp.content)
    except Exception:
        return {}
