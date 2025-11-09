"""This script processes JSON files containing equipment data and
creates analogous relationships between nodes in a Neo4j database."""
import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv
from src.utils.log import logger

# Neo4j connection details

load_dotenv()

uri = os.environ.get("NEO4J_URI")
username = os.environ.get("NEO4J_USERNAME")
password = os.environ.get("NEO4J_PASSWORD")
database_name = os.environ.get("NEO4J_DATABASE")


def _setup_config():
    """Setup the configuration for the script."""
    ROOT_FOLDER_PATH = os.path.abspath("")    # pylint: disable=invalid-name
    CONFIG_FILE_PATH = ROOT_FOLDER_PATH + \
        "/data/configs/config.json"    # pylint: disable=invalid-name
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    ADM_FOLDER_PATH = os.path.join(    # pylint: disable=invalid-name
        ROOT_FOLDER_PATH, config["analogous_to_adm_folder_path"])
    config["ADM_FOLDER_PATH"] = ADM_FOLDER_PATH
    return config


# Create Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password), database=database_name)


def _create_nodes_and_relationships(tx, data):
    """Create nodes and relationships in the Neo4j database."""

    # Create DataSheet node
    meta_data = data.get("meta_data", {})
    data_sheet_uuid = meta_data.get("uuid", "")
    logger.info(f"Creating DataSheet: {data_sheet_uuid}")
    tx.run(
        "MERGE (ds:DataSheet {uuid: $uuid}) SET ds += $properties",
        uuid=data_sheet_uuid,
        properties=meta_data,
    )

    # Create Equipment nodes and relationships
    for equipment in data.get("equipments", []):
        logger.info(
            f"""Creating Equipment: {equipment['uuid']} {
                equipment.get('equipment_tag', '')}"""
        )
        equipment["data_sheet_uuid"] = data_sheet_uuid
        tx.run(
            "MERGE (eq:Equipment {uuid: $uuid}) SET eq += $properties",
            uuid=equipment["uuid"],
            properties=equipment,
        )

    # Create SubPart nodes and relationships
    for sub_part in data.get("sub_parts", []):
        logger.info(
            f"Creating SubPart: {sub_part['uuid']} {sub_part.get('subpart_name', '')}"
        )
        sub_part["data_sheet_uuid"] = data_sheet_uuid
        tx.run(
            "MERGE (sp:SubPart {uuid: $uuid}) SET sp += $properties",
            uuid=sub_part["uuid"],
            properties=sub_part,
        )
        logger.info("Creating relationship between Equipment and SubPart")
        tx.run(
            "MATCH (eq:Equipment), (sp:SubPart)"
            "WHERE eq.data_sheet_uuid = sp.data_sheet_uuid "
            "MERGE (eq)-[:HAS_SUBPART]->(sp)",
        )

    # Create Nozzle nodes and relationships
    for nozzle in data.get("nozzles", []):
        logger.info(
            f"Creating Nozzle: {nozzle['uuid']} {nozzle.get('subpart_name', '')}"
        )
        nozzle["data_sheet_uuid"] = data_sheet_uuid
        tx.run(
            "MERGE (nz:Nozzle {uuid: $uuid}) SET nz += $properties",
            uuid=nozzle["uuid"],
            properties=nozzle,
        )

        tx.run(
            "MATCH (sp:SubPart), (nz:Nozzle)"
            "WHERE sp.data_sheet_uuid = nz.data_sheet_uuid AND sp.subpart_name = nz.subpart_name "
            "MERGE (sp)-[:HAS_NOZZLE]->(nz)",
        )


def create_analogous_relationships(tx, mode="both"):
    """
    Create or update analogous relationships between nodes in the Neo4j database,
    with properties indicating mismatches or complementary properties.

    mode:
    - "mismatch": Handle only mismatches.
    - "complementary": Handle only complementary properties.
    - "both": Handle both mismatches and complementary properties.
    """

    def _compare_and_create_relationship(node_label, match_conditions):
        """
        Compare properties between nodes and create or update analogous relationships
        with mismatch or complementary properties based on the mode.
        """

        match_condition_str = " AND ".join(
            [f"n1.{cond} = n2.{cond}" for cond in match_conditions]
        )

        query = f"""
        MATCH (n1:{node_label}), (n2:{node_label})
        WHERE {match_condition_str} AND id(n1) < id(n2)
        WITH n1, n2
        OPTIONAL MATCH (n1)-[r:ANALOGOUS_TO]-(n2)
        WITH n1, n2, r
        CALL {{
            WITH n1, n2
            UNWIND keys(n1) AS key
            WITH key, n1[key] AS value1, n2[key] AS value2, n1.data_sheet_uuid AS uuid1,
            n2.data_sheet_uuid AS uuid2
            OPTIONAL MATCH (ds1:DataSheet {{uuid: uuid1}}), (ds2:DataSheet {{uuid: uuid2}})
            RETURN collect(
                CASE
                    WHEN value1 IS NULL AND value2 IS NOT NULL AND '{mode}' IN
                    ['complementary', 'both'] THEN
                        {{key: key, value: value2 + \
                            " (complementary from " + ds2.file_name + " to " + ds1.file_name + ")"}}
                    WHEN value2 IS NULL AND value1 IS NOT NULL AND '{mode}' IN
                    ['complementary', 'both'] THEN
                        {{key: key, value: value1 + \
                            " (complementary from " + ds1.file_name + " to " + ds2.file_name + ")"}}
                    WHEN value1 <> value2 AND '{mode}' IN ['mismatch', 'both'] THEN
                        {{key: key, value: "mismatch"}}
                    ELSE NULL
                END
            ) AS property_differences
        }}
        WITH n1, n2, r, [pd IN property_differences WHERE pd IS NOT NULL] AS prop_diffs
        FOREACH (_ IN CASE WHEN r IS NULL THEN [1] ELSE [] END |
            MERGE (n1)-[new_r:ANALOGOUS_TO]->(n2)
            SET new_r += apoc.map.fromPairs([p in prop_diffs | [p.key, p.value]])
            REMOVE new_r.data_sheet_uuid
        )
        FOREACH (_ IN CASE WHEN r IS NOT NULL THEN [1] ELSE [] END |
            SET r += apoc.map.fromPairs([p in prop_diffs | [p.key, p.value]])
            REMOVE r.data_sheet_uuid
        )
        """

        logger.info(
            f"""Creating or updating analogous relationships for {
                node_label} with mode '{mode}'"""
        )
        tx.run(query)

    # Compare Equipment nodes
    _compare_and_create_relationship("Equipment", ["equipment_tag"])

    # Compare Nozzle nodes (based on both connection_type and subpart_name)
    _compare_and_create_relationship("Nozzle", ["connection_type", "subpart_name"])

    # Compare SubPart nodes
    _compare_and_create_relationship("SubPart", ["subpart_name"])


def _process_json_file(file_path):
    """Process a JSON file and create nodes and relationships in the Neo4j database."""
    # Load JSON data from file
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Process the JSON data
    with driver.session() as session:
        session.write_transaction(_create_nodes_and_relationships, data)


def main():
    """Main"""
    config = _setup_config()
    folder_path = config["ADM_FOLDER_PATH"]

    # Process all JSON files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            logger.info(f"INIT: Processing file: [bold]{file_path}[/bold]")
            _process_json_file(file_path)
            logger.info(f"DONE: Processing file: [bold]{file_path}[/bold]")

    # Create analogous relationships
    mode = "both"  # Change this to "mismatch", "complementary", or "both" as needed
    with driver.session() as session:
        session.write_transaction(create_analogous_relationships, mode)


if __name__ == "__main__":
    main()
