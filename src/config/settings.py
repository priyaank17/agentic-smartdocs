"""Centralized runtime configuration."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Azure
    azure_document_intelligence_endpoint: str = Field(
        ..., env="AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT",
        description="Endpoint for the custom Azure Document Intelligence model",
    )
    azure_document_intelligence_key: str = Field(
        ..., env="AZURE_DOCUMENT_INTELLIGENCE_KEY",
        description="API key for the custom Azure Document Intelligence model",
    )

    # Paligemma / vLLM
    paligemma_model_name: str = Field(
        "paligemma-3b", env="PALIGEMMA_MODEL_NAME",
        description="Model name or path loaded by vLLM",
    )
    paligemma_lora_path: Optional[str] = Field(
        None, env="PALIGEMMA_LORA_PATH", description="Optional LoRA checkpoint path",
    )
    vllm_host: str = Field("0.0.0.0", env="VLLM_HOST")
    vllm_port: int = Field(9000, env="VLLM_PORT")

    # Neo4j
    neo4j_uri: str = Field(..., env="NEO4J_URI")
    neo4j_user: str = Field(..., env="NEO4J_USER")
    neo4j_password: str = Field(..., env="NEO4J_PASSWORD")

    # Storage & misc
    storage_account: Optional[str] = Field(None, env="STORAGE_ACCOUNT")
    storage_container: Optional[str] = Field(None, env="STORAGE_CONTAINER")
    landing_ai_api_key: Optional[str] = Field(
        "aGViZ25yZ3poYWV2eHhxb2ZvZ2U5OktOZDlobmFUWmJPT3llcnJ1UHpiT1ZFVkR0MW9kVnd5",
        env="VA_API_KEY",
        description="Landing AI Agentic Document Analysis API key",
    )
    skip_classifier: bool = Field(False, env="SKIP_CLASSIFIER")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
