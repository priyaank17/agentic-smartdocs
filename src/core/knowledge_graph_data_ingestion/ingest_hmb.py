"""This module contains functions to ingest data into the knowledge graph"""
import time
from src.utils.neo4j_connector import Neo4jConnection


def _create_or_update_hmb_node(tx, meta_data, additional_properties):
    """This function creates or updates an HMB node"""
    query = """
    MERGE (h:HMB {id: $id})
    SET h += $meta_data
    SET h.adm_ingestion_starting_timestamp = $adm_ingestion_starting_timestamp,
        h.adm_ingestion_ending_timestamp = $adm_ingestion_ending_timestamp,
        h.adm_ingestion_status = $adm_ingestion_status
    RETURN h
    """
    ap = additional_properties
    result = tx.run(query,
                    id=meta_data['id'],
                    meta_data=meta_data,
                    adm_ingestion_starting_timestamp=ap['adm_ingestion_starting_timestamp'],
                    adm_ingestion_ending_timestamp=ap['adm_ingestion_ending_timestamp'],
                    adm_ingestion_status=ap['adm_ingestion_status'])
    return result.single()


def _create_or_update_stream_node(tx, stream_number, properties, hmb_id):
    """This function creates or updates a stream node and creates a relationship to HMB"""
    query = """
    MERGE (s:Stream {stream_number: $stream_number, source: $source})
    SET s += $properties
    RETURN s
    """
    source = "HMB" + "_" + hmb_id
    words = source.split()
    source = "_".join(words).lower()
    result = tx.run(query, stream_number=stream_number,
                    properties=properties, hmb_id=hmb_id, source=source)
    return result.single()


def _process_hmb_data(hmb_data, neo4j_connection, start_time, end_time, ingestion_status):
    """This function processes HMB data and extracts information"""
    if isinstance(hmb_data, dict):
        meta_data = hmb_data.get("meta_data", {})
        hmb_id = meta_data.get("id")
        if hmb_id:
            additional_properties = {
                'adm_ingestion_starting_timestamp': start_time,
                'adm_ingestion_ending_timestamp': end_time,
                'adm_ingestion_status': ingestion_status
            }
            neo4j_connection.execute_write(
                _create_or_update_hmb_node, meta_data, additional_properties)
        for stream in hmb_data.get("streams", []):
            stream_number = stream.get("stream_number")
            if stream_number:
                properties = {}
                for condition in stream.get("operating_conditions", []):
                    state = condition.get("state")
                    for prop in condition.get("properties", []):
                        prop_name = f"{prop['name']} ({state})"
                        properties[prop_name] = prop.get("value")
                neo4j_connection.execute_write(
                    _create_or_update_stream_node, stream_number, properties, hmb_id)
    else:
        print(f"Unexpected data structure in HMB data: {hmb_data}")


def ingest_hmb(hmb_data, database_name, plant_id):
    """This function ingests HMB data into the knowledge graph"""
    neo4j_connection = Neo4jConnection(database_name)
    neo4j_connection.connect()
    # Record ingestion start time
    start_time = time.time() * 1000  # Current time in milliseconds

    # Process the HMB data
    _process_hmb_data(hmb_data, neo4j_connection, start_time, None, "INGESTING")

    # Record ingestion end time
    end_time = time.time() * 1000  # Current time in milliseconds

    # Update HMB node with end time and status
    if isinstance(hmb_data, dict):
        meta_data = hmb_data.get("meta_data", {})
        meta_data["plant_id"] = plant_id  # Add plant_id to meta_data
        hmb_id = meta_data.get("id")
        if hmb_id:
            additional_properties = {
                'adm_ingestion_starting_timestamp': start_time,
                'adm_ingestion_ending_timestamp': end_time,
                'adm_ingestion_status': "INGESTING_COMPLETED"
            }
            neo4j_connection.execute_write(
                _create_or_update_hmb_node, meta_data, additional_properties)

    # Close the connection
    neo4j_connection.close()


if __name__ == "__main__":
    ingest_hmb(hmb_data="", database_name="", plant_id="")
