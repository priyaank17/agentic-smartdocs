"""FastAPI for orchestrating PID Parsing steps."""

import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.utils.log import logger
from src.constants.Actions import Actions
from src.utils.token import set_token

from src.events import (
    handle_EXTRACT_CONTROL_NARRATIVE_DATA,
    handle_EXTRACT_HMB_DOCUMENT_DATA,
    handle_GET_LIST_OF_DOCUMENTS,
    handle_INGEST_DATA_SHEET_ADM_INTO_NEO4J,
    handle_EXTRACT_PROCESS_NARRATIVE_DATA,
    handle_EXTRACT_PROCESS_NARRATIVE_RAG_DATA,
    handle_EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA,
    handle_EXTRACT_CONTROL_NARRATIVE_RAG_JUNIOR_DATA,
    handle_TRIGGERED_PROCESS_NARRATIVE_RAG_JUNIOR_DATA_ACTION,
    handle_TRIGGERED_DATA_SHEET_DATA_ACTION,
    handle_TRIGGERED_CONTROL_NARRATIVE_DATA_ACTION,
    handle_EXTRACT_DATA_SHEET_DATA,
    handle_EXTRACT_DATA_SHEET_DATA_V2,
    handle_EXTRACT_CAUSE_AND_EFFECT_DATA,
    handle_INGEST_PFD_INTO_NEO4J,
    handle_INGEST_HMB_INTO_NEO4J,
    handle_INGEST_PROCESS_NARRATIVE_ADM_INTO_NEO4J,
    handle_INGEST_CONTROL_NARRATIVE_ADM_INTO_NEO4J,
    handle_GET_DATA_SHEET_STANDARD_DETAILS,
    handle_CHECK_DOCUMENT_STATUS,
)

app = FastAPI()
logging.getLogger("azure").setLevel(logging.WARNING)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://artisan.drishya.ai",
        "https://data-explorer.drishya.ai",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    """
    A Pydantic BaseModel class representing an API Gateway event.

    Attributes:
        action (str): The action or HTTP method of the event.
        body (dict, optional): The request body payload. Defaults to None.
        queryStringParameters (dict, optional): Query string parameters
        from the URL. Defaults to None.
    """
    action: str
    body: dict = None
    queryStringParameters: dict = None


def _resolve_params(event: Event):
    params = event.dict()
    is_api_event = False
    if event.body and isinstance(event.body, str):
        params = json.loads(event.body)
        is_api_event = True
    elif event.body:
        params = event.body
    elif event.queryStringParameters:
        params = event.queryStringParameters
    return params, is_api_event


# pylint: disable=too-many-branches, too-many-statements
@app.post("/lambda_handler")
async def lambda_handler(event: Event, request: Request):  # noqa: C901
    """Lambda Handler"""
    logger.info("INIT: Lambda Handler")
    logger.info("Event: %s", event)
    try:
        action = (
            event.action if hasattr(event, 'action')
            else event.body.get('action') if event.body
            else None
        )
        if not action:
            raise HTTPException(status_code=400, detail="Action key not found in request")

        params = event.body if event.body else {}
        print(params)
        params, is_api_event = _resolve_params(event)
        if isinstance(params, str):
            params = json.loads(params)

        if 'action' not in params:
            params['action'] = action

        result = {
            "success": False,
            "msg": f"Action {action} is not valid",
        }
        auth_token = request.headers.get("Authorization")
        set_token(auth_token)

        if action == Actions.GET_LIST_OF_DOCUMENTS:
            result = await handle_GET_LIST_OF_DOCUMENTS(is_api_event, event.body)
        elif action == Actions.INGEST_DATA_SHEET_ADM_INTO_NEO4J:
            result = await handle_INGEST_DATA_SHEET_ADM_INTO_NEO4J(True, params)
        elif action == Actions.INGEST_HMB_INTO_NEO4J:
            result = await handle_INGEST_HMB_INTO_NEO4J(True, params)
        elif action == Actions.INGEST_PFD_INTO_NEO4J:
            result = await handle_INGEST_PFD_INTO_NEO4J(True, params)
        elif action == Actions.INGEST_PROCESS_NARRATIVE_ADM_INTO_NEO4J:
            result = await handle_INGEST_PROCESS_NARRATIVE_ADM_INTO_NEO4J(True, params)
        elif action == Actions.EXTRACT_CONTROL_NARRATIVE_DATA:
            result = await handle_EXTRACT_CONTROL_NARRATIVE_DATA(params)
        elif action == Actions.EXTRACT_HMB_DOCUMENT_DATA:
            result = await handle_EXTRACT_HMB_DOCUMENT_DATA(params)
        elif action == Actions.EXTRACT_PROCESS_NARRATIVE_DATA:
            result = await handle_EXTRACT_PROCESS_NARRATIVE_DATA(params)
        elif action == Actions.EXTRACT_PROCESS_NARRATIVE_RAG_DATA:
            result = await handle_EXTRACT_PROCESS_NARRATIVE_RAG_DATA(params)
        elif action == Actions.TRIGGERED_PROCESS_NARRATIVE_RAG_JUNIOR_DATA_ACTION:
            result = await handle_TRIGGERED_PROCESS_NARRATIVE_RAG_JUNIOR_DATA_ACTION(params)
        elif action == Actions.TRIGGERED_DATA_SHEET_DATA_ACTION:
            result = await handle_TRIGGERED_DATA_SHEET_DATA_ACTION(params)
        elif action == Actions.TRIGGERED_CONTROL_NARRATIVE_DATA_ACTION:
            result = await handle_TRIGGERED_CONTROL_NARRATIVE_DATA_ACTION(params)
        elif action == Actions.EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA:
            result = await handle_EXTRACT_PROCESS_NARRATIVE_RAG_JUNIOR_DATA(params)
        elif action == Actions.EXTRACT_CONTROL_NARRATIVE_RAG_JUNIOR_DATA:
            result = await handle_EXTRACT_CONTROL_NARRATIVE_RAG_JUNIOR_DATA(params)
        elif action == Actions.EXTRACT_DATA_SHEET_DATA:
            result = await handle_EXTRACT_DATA_SHEET_DATA(params)
        elif action == Actions.EXTRACT_DATA_SHEET_DATA_V2:
            result = await handle_EXTRACT_DATA_SHEET_DATA_V2(params)
        elif action == Actions.GET_DATA_SHEET_STANDARD_DETAILS:
            result = await handle_GET_DATA_SHEET_STANDARD_DETAILS(params)
        elif action == Actions.EXTRACT_CAUSE_AND_EFFECT_DATA:
            result = await handle_EXTRACT_CAUSE_AND_EFFECT_DATA(params)
        elif action == Actions.INGEST_CONTROL_NARRATIVE_ADM_INTO_NEO4J:
            result = await handle_INGEST_CONTROL_NARRATIVE_ADM_INTO_NEO4J(True, params)
        elif action == Actions.CHECK_DOCUMENT_STATUS:
            result = await handle_CHECK_DOCUMENT_STATUS(params)

    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    finally:
        set_token(None)

    logger.info("DONE: Lambda Handler")
    return result
