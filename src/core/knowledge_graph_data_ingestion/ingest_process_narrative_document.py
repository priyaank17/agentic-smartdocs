"""This module contains the function to ingest the Process Narrative Document (PND) data."""
import time
from src.utils.neo4j_connector import Neo4jConnection
from src.utils.log import logger


def _flatten_properties(properties):
    """Flatten nested properties into a single dictionary with keys.."""
    flat_properties = {}
    for key, value in properties.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat_properties[f"{key}_{sub_key}"] = sub_value
        else:
            flat_properties[key] = value
    return flat_properties


def _create_or_update_pnd_node(tx, meta_data, additional_properties):
    """This function creates or updates a PND node"""
    query = """
    MERGE (p:PND {id: $id})
    SET p += $meta_data
    SET p.adm_ingestion_starting_timestamp = $adm_ingestion_starting_timestamp,
        p.adm_ingestion_ending_timestamp = $adm_ingestion_ending_timestamp,
        p.adm_ingestion_status = $adm_ingestion_status
    RETURN p
    """
    ap = additional_properties
    result = tx.run(query,
                    id=meta_data['id'],
                    meta_data=meta_data,
                    adm_ingestion_starting_timestamp=ap['adm_ingestion_starting_timestamp'],
                    adm_ingestion_ending_timestamp=ap['adm_ingestion_ending_timestamp'],
                    adm_ingestion_status=ap['adm_ingestion_status'])
    return result.single()


def _create_or_update_connection_node(tx, connection_id, properties, pnd_id, pnd_meta_data):
    """This function creates or updates a connection node and creates a relationship to PND"""
    query = """
    MERGE (c:Connection {id: $connection_id, source: $source, connection_id: $connection_id})
    SET c += $properties
    SET c += $pnd_meta_data
    RETURN c
    """
    source = "PND" + "_" + pnd_id
    flat_properties = _flatten_properties(properties)
    data = pnd_meta_data
    result = tx.run(query, connection_id=connection_id,
                    properties=flat_properties, pnd_id=pnd_id, pnd_meta_data=data, source=source)
    return result.single()


def _process_pnd_data(pnd_data, neo4j_connection, start_time, end_time, ingestion_status):
    """This function processes PND data and extracts information"""
    if isinstance(pnd_data, dict):
        # Extract and create/update PND node
        meta_data = pnd_data.get("meta_data", {})
        pnd_id = meta_data.get("id")
        if pnd_id:
            additional_properties = {
                'adm_ingestion_starting_timestamp': start_time,
                'adm_ingestion_ending_timestamp': end_time,
                'adm_ingestion_status': ingestion_status
            }
            neo4j_connection.execute_write(
                _create_or_update_pnd_node, meta_data, additional_properties)
            logger.info(f"Processed PND node with id: {pnd_id}")

        # Process connections and create/update connection nodes with relationship to PND
        for idx, connection in enumerate(pnd_data.get("connections", [])):
            properties = {key: connection[key] for key in connection}
            # Unique ID for each connection based on PND ID and index
            connection_id = f"{pnd_id}_{idx}"
            try:
                # Execute the query to create or update the connection node
                neo4j_connection.execute_write(
                    _create_or_update_connection_node, connection_id, properties, pnd_id, meta_data)
                logger.info(f"""Processed connection {
                            connection_id} for PND id: {pnd_id}""")
            except BaseException as e:
                logger.error(f"""Error processing connection {
                             connection_id} for PND id: {pnd_id}: {e}""")
    else:
        logger.error(f"Unexpected data structure in PND data: {pnd_data}")


def ingest_process_narrative_document(pnd_data, database_name, plant_id):
    """This function ingests the Process Narrative Document (PND) data into the knowledge graph"""
    neo4j_connection = Neo4jConnection(database_name)
    neo4j_connection.connect()

    # Record ingestion start time
    start_time = time.time() * 1000  # Current time in milliseconds

    # Process the PND data
    _process_pnd_data(pnd_data, neo4j_connection, start_time, None, "INGESTING")

    # Record ingestion end time
    end_time = time.time() * 1000  # Current time in milliseconds

    # Update PND node with end time and status
    if isinstance(pnd_data, dict):
        meta_data = pnd_data.get("meta_data", {})
        pnd_id = meta_data.get("id")
        meta_data["plant_id"] = plant_id
        if pnd_id:
            additional_properties = {
                'adm_ingestion_starting_timestamp': start_time,
                'adm_ingestion_ending_timestamp': end_time,
                'adm_ingestion_status': "INGESTING_COMPLETED"
            }
            neo4j_connection.execute_write(
                _create_or_update_pnd_node, meta_data, additional_properties)
            logger.info(f"""Updated PND node with id: {
                        pnd_id} to status: INGESTING_COMPLETED""")

    # Close the connection
    neo4j_connection.close()


if __name__ == "__main__":
    ingest_process_narrative_document(pnd_data="", database_name="", plant_id="")
