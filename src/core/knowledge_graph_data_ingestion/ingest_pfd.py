"""This module provides functionality to ingest Process Flow Diagram (PFD) data"""
import time
from src.utils.neo4j_connector import Neo4jConnection


def _create_or_update_pfd_node(tx, meta_data, additional_properties):
    """This function creates or updates a PFD node"""
    query = """
    MERGE (p:PFD {uuid: $uuid})
    SET p += $meta_data
    SET p.adm_ingestion_starting_timestamp = $adm_ingestion_starting_timestamp,
        p.adm_ingestion_ending_timestamp = $adm_ingestion_ending_timestamp,
        p.adm_ingestion_status = $adm_ingestion_status
    RETURN p
    """
    ap = additional_properties
    result = tx.run(query,
                    uuid=meta_data['uuid'],
                    meta_data=meta_data,
                    adm_ingestion_starting_timestamp=ap['adm_ingestion_starting_timestamp'],
                    adm_ingestion_ending_timestamp=ap['adm_ingestion_ending_timestamp'],
                    adm_ingestion_status=ap['adm_ingestion_status'])
    return result.single()


def _create_or_update_stream_node(tx, stream_number, properties, pfd_uuid):
    """This function creates or updates a stream node and creates a relationship to PFD"""
    query = """
    CREATE (s:Stream {stream_number: $stream_number, source: $source})
    SET s += $properties
    RETURN s
    """
    source = "pfd" + "_" + pfd_uuid
    words = source.split()
    source = "_".join(words).lower()
    result = tx.run(query, stream_number=stream_number,
                    properties=properties, pfd_uuid=pfd_uuid, source=source)
    return result.single()


def _process_pfd_data(pfd_data, neo4j_connection, start_time, end_time, ingestion_status):
    """This function processes PFD data and extracts information"""
    if isinstance(pfd_data, dict):
        # Extract and create/update PFD node
        meta_data = pfd_data.get("meta_data", {})
        pfd_uuid = meta_data.get("uuid")
        if pfd_uuid:
            additional_properties = {
                'adm_ingestion_starting_timestamp': start_time,
                'adm_ingestion_ending_timestamp': end_time,
                'adm_ingestion_status': ingestion_status
            }
            neo4j_connection.execute_write(
                _create_or_update_pfd_node, meta_data, additional_properties)

        # Process streams and create/update stream nodes with relationship to PFD
        for stream in pfd_data.get("streams", []):
            stream_number = stream.get("stream_number")
            if stream_number:
                properties = {key: stream[key]
                              for key in stream if key != "stream_number"}

                # Execute the query to create or update the stream node
                neo4j_connection.execute_write(
                    _create_or_update_stream_node, stream_number, properties, pfd_uuid)
    else:
        print(f"Unexpected data structure in PFD data: {pfd_data}")


def ingest_pfd(pfd_data, database_name, plant_id):
    """This function ingests the Process Flow Diagram (PFD) data into the knowledge graph"""
    neo4j_connection = Neo4jConnection(database_name)
    neo4j_connection.connect()

    # Record ingestion start time
    start_time = time.time() * 1000  # Current time in milliseconds

    # Process the PFD data
    _process_pfd_data(pfd_data, neo4j_connection, start_time, None, "INGESTING")

    # Record ingestion end time
    end_time = time.time() * 1000  # Current time in milliseconds

    # Update PFD node with end time and status
    if isinstance(pfd_data, dict):
        meta_data = pfd_data.get("meta_data", {})
        meta_data["plant_id"] = plant_id
        pfd_uuid = meta_data.get("uuid")
        if pfd_uuid:
            additional_properties = {
                'adm_ingestion_starting_timestamp': start_time,
                'adm_ingestion_ending_timestamp': end_time,
                'adm_ingestion_status': "INGESTING_COMPLETED"
            }
            neo4j_connection.execute_write(
                _create_or_update_pfd_node, meta_data, additional_properties)

    # Close the connection
    neo4j_connection.close()


if __name__ == "__main__":
    ingest_pfd(pfd_data="", database_name="", plant_id="")
