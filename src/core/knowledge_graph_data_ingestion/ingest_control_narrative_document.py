"""This module contains functions to ingest Control Narrative data."""
import time
from src.utils.neo4j_connector import Neo4jConnection


def _create_or_update_cn_node(tx, meta_data, additional_properties):
    """This function creates or updates a Control Narrative (CN) node"""
    query = """
    MERGE (c:ControlNarrative {id: $id})
    SET c += $meta_data
    SET c.adm_ingestion_starting_timestamp = $adm_ingestion_starting_timestamp,
        c.adm_ingestion_ending_timestamp = $adm_ingestion_ending_timestamp,
        c.adm_ingestion_status = $adm_ingestion_status
    RETURN c
    """
    ap = additional_properties
    result = tx.run(query,
                    id=meta_data['id'],
                    meta_data=meta_data,
                    adm_ingestion_starting_timestamp=ap['adm_ingestion_starting_timestamp'],
                    adm_ingestion_ending_timestamp=ap['adm_ingestion_ending_timestamp'],
                    adm_ingestion_status=ap['adm_ingestion_status'])
    return result.single()


def _create_or_update_instrument_node(tx, instrument_data, cn_id, cn_meta_data):
    """This function creates or updates an Instrument node."""
    query = """
    MERGE (i:Instrument {instrument_id: $instrument_id, source: $source})
    SET i += $instrument_data
    SET i += $cn_meta_data
    RETURN i
    """
    source = cn_meta_data['adm_type'] + "_" + cn_meta_data['document_number']
    words = source.split()
    source = "_".join(words).lower()
    cn = cn_meta_data
    result = tx.run(query, instrument_id=instrument_data['instrument_id'],
                    instrument_data=instrument_data, cn_id=cn_id, cn_meta_data=cn, source=source)
    return result.single()


def _create_or_update_control_loop_node(tx, control_loop_data, cn_id, cn_meta_data):
    """This function creates or updates a Control Loop node"""
    query = """
    MERGE (cl:ControlLoop {control_loop_id: $control_loop_id, source: $source})
    SET cl += $control_loop_data
    SET cl += $cn_meta_data
    RETURN cl
    """
    source = cn_meta_data['adm_type'] + "_" + cn_meta_data['document_number']
    words = source.split()
    source = "_".join(words).lower()
    cn = cn_meta_data
    data = control_loop_data
    result = tx.run(query, control_loop_id=control_loop_data['control_loop_id'],
                    control_loop_data=data, cn_id=cn_id, cn_meta_data=cn, source=source)
    return result.single()


def _process_cn_data(cn_data, neo4j_connection, start_time, end_time, ingestion_status):
    """This function processes Control Narrative data and extracts information"""
    if isinstance(cn_data, dict):
        # Extract and create/update Control Narrative node
        meta_data = cn_data.get("meta_data", {})
        cn_id = meta_data.get("id")
        if cn_id:
            additional_properties = {
                'adm_ingestion_starting_timestamp': start_time,
                'adm_ingestion_ending_timestamp': end_time,
                'adm_ingestion_status': ingestion_status
            }
            neo4j_connection.execute_write(
                _create_or_update_cn_node, meta_data, additional_properties)

        # Process data and create/update Instrument or Control Loop nodes with relationship to CN
        for item in cn_data.get("data", []):
            if 'instrument_id' in item:
                neo4j_connection.execute_write(
                    _create_or_update_instrument_node, item, cn_id, meta_data)
            elif 'control_loop_id' in item:
                neo4j_connection.execute_write(
                    _create_or_update_control_loop_node, item, cn_id, meta_data)
            else:
                print(f"Unexpected data structure in item: {item}")
    else:
        print(f"Unexpected data structure in Control Narrative data: {cn_data}")


def ingest_control_narrative_document(cn_data, database_name, plant_id):
    """This function ingests the Control Narrative data into the knowledge graph"""
    neo4j_connection = Neo4jConnection(database_name)
    neo4j_connection.connect()

    # Record ingestion start time
    start_time = time.time() * 1000  # Current time in milliseconds

    # Process the Control Narrative data
    _process_cn_data(cn_data, neo4j_connection, start_time, None, "INGESTING")

    # Record ingestion end time
    end_time = time.time() * 1000  # Current time in milliseconds

    # Update Control Narrative node with end time and status
    if isinstance(cn_data, dict):
        meta_data = cn_data.get("meta_data", {})
        cn_id = meta_data.get("id")
        meta_data["plant_id"] = plant_id
        if cn_id:
            additional_properties = {
                'adm_ingestion_starting_timestamp': start_time,
                'adm_ingestion_ending_timestamp': end_time,
                'adm_ingestion_status': "INGESTING_COMPLETED"
            }
            neo4j_connection.execute_write(
                _create_or_update_cn_node, meta_data, additional_properties)

    # Close the connection
    neo4j_connection.close()


if __name__ == "__main__":
    ingest_control_narrative_document(cn_data="", database_name="", plant_id="")
