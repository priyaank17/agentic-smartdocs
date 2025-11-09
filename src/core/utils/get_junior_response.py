"""This module contains functions to extract data sheet data in Local"""

import os
import json
import requests
from src.utils.log import logger
from src.utils.token import get_token


def get_document_data_from_junior_app_runner(
    model_name, api_input, chat_history, session_id
):
    """Returns the response from the Junior App Runner."""
    logger.info("Init: Extracting narrative data using Junior API")
    junior_api_url = os.environ.get("JUNIOR_API_URL", "")
    token = get_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    body = {
        "input": {
            "question": api_input,
            "chat_history": chat_history or [],
            "session_id": session_id,
        },
        "config": {
            "configurable": {
                "llm_model": model_name,  # 'gpt-4o',
            },
        },
    }
    response = requests.post(
        junior_api_url, headers=headers, data=json.dumps(body), timeout=60
    )
    if response.status_code == 200:
        logger.info("Done: Extracting data using Junior API")
    else:
        logger.error(
            f"Error: Extracting data using Junior API {response.status_code}"
        )
    return response
