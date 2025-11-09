"""
This module provides functionality to ingest process narrative documents into knowledge graph
"""

import os
from src.utils.log import logger

from src.knowledge_graph_data_ingestion import (
    ingest_process_narrative_document,
)
from src.events.utils import get_return_type

from src.graphql.utils import get_graph_ql_status, update_graph_ql_status
from src.constants import DatabaseStatus
from src.utils.neo4j_connector import Neo4jConnection
from src.utils.storage_utils import fetch_file_via_adapter


async def handle_INGEST_PROCESS_NARRATIVE_ADM_INTO_NEO4J(
    is_api_event, payload
):  # pylint: disable=invalid-name
    """
    Asynchronously handles the ingestion of process narrative documents into Neo4j.
    """
    logger.info("INIT: Ingest Process Narrative ADM into neo4j")
    # if the validation fails there would be an exception and it would be handled at lambda handler
    # validate(instance=payload, schema=schemas[Actions.INGEST_DATA_SHEET_ADM_INTO_NEO4J.__str__()])
    adm_path, plant_id = payload["adm_path"], payload["plant_id"]
    step_status_graph_ql = await get_graph_ql_status(plant_id)
    if step_status_graph_ql["success"]:
        await update_graph_ql_status(plant_id, DatabaseStatus.INGESTING_PROCESS_NARRATIVE_ADM)

    file_path = adm_path
    bucket_name = os.getenv("BUCKET")
    logger.info(f"INIT: Reading adm from {bucket_name}/{file_path}")
    adm = await fetch_file_via_adapter(bucket_name, file_path)
    try:
        database_name = await Neo4jConnection.get_database_name(plant_id)
        ingest_process_narrative_document(adm, database_name, plant_id)
        step_status_graph_ql = await get_graph_ql_status(plant_id)
        if step_status_graph_ql["success"]:
            await update_graph_ql_status(
                plant_id, DatabaseStatus.INGESTING_PROCESS_NARRATIVE_ADM_SUCCESSFUL
            )
        step_status = {"success": True, "data": {"plant_id": plant_id}}
    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.error(f"ERROR: Ingesting adm Failed: {e}")
        await update_graph_ql_status(
            plant_id, DatabaseStatus.INGESTING_PROCESS_NARRATIVE_ADM_FAILED
        )
        step_status = {"success": False, "error": str(e)}

    logger.info("DONE: Ingest Process Narrative ADM into neo4j")
    return get_return_type(is_api_event, step_status)
