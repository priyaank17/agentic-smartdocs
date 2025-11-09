"""
This module provides utilities for working with various language models
and embeddings.

It includes functions for setting up Azure OpenAI models, and manages
API key retrieval.
"""

import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()


def _get_azure_openai_model(deployment_name):
    """
    Initialize and configure the Azure OpenAI model.

    Returns:
        AzureChatOpenAI: Configured Azure OpenAI language model.
    """
    llm = AzureChatOpenAI(
        azure_deployment=deployment_name,
        api_version=os.getenv("OPENAI_GPT_4O_API_VERSION")
    )
    return llm


def get_llm_model(vendor="azure", model_name="gpt-4o"):
    """
    Select and return the specified language model.
    Currently supports Azure OpenAI models.
    """
    print(model_name)
    if vendor == "azure":
        llm = _get_azure_openai_model(model_name)
        return llm
    return None
