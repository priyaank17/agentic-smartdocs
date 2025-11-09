"""Script to create CSV files for nodes and relationships in the Neo4j database."""

import os
import csv
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from src.utils.log import logger

load_dotenv()

uri = os.environ.get("NEO4J_URI")
username = os.environ.get("NEO4J_USERNAME")
password = os.environ.get("NEO4J_PASSWORD")
database_name = os.environ.get("NEO4J_DATABASE")


driver = GraphDatabase.driver(uri, auth=(username, password), database=database_name)


def _setup_config():
    """Setup the configuration for the script."""
    ROOT_FOLDER_PATH = os.path.abspath("")  # pylint: disable=invalid-name
    # pylint: disable=invalid-name
    CONFIG_FILE_PATH = (
        ROOT_FOLDER_PATH + "/data/configs/config.json"
    )
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    NODES_CSV_PATH = os.path.join(  # pylint: disable=invalid-name
        ROOT_FOLDER_PATH, config["nodes_csv_path"]
    )
    config["NODES_CSV_PATH"] = NODES_CSV_PATH
    RELATIONSHIPS_CSV_PATH = os.path.join(  # pylint: disable=invalid-name
        ROOT_FOLDER_PATH, config["relationships_csv_path"]
    )
    config["RELATIONSHIPS_CSV_PATH"] = RELATIONSHIPS_CSV_PATH
    return config


def fetch_nodes(tx):
    """Fetch nodes from the Neo4j database."""
    query = """
    MATCH (n)
    RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties
    """
    result = tx.run(query)
    logger.info("Fetched nodes from the Neo4j database.")
    return [record for record in result]  # pylint: disable=unnecessary-comprehension


def fetch_relationships(tx):
    """Fetch relationships from the Neo4j database."""
    query = """
    MATCH (n)-[r]->(m)
    RETURN id(r) AS rel_id, id(n) AS start_id, id(m) AS end_id, type(r) AS type, properties(r) AS properties
    """
    result = tx.run(query)
    logger.info("Fetched relationships from the Neo4j database.")
    return [record for record in result]  # pylint: disable=unnecessary-comprehension


def generate_data():
    """Create CSV files for nodes and relationships in the Neo4j database."""
    with driver.session() as session:
        nodes = session.read_transaction(fetch_nodes)
        config = _setup_config()
        with open(config["NODES_CSV_PATH"], "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "labels", "properties"])
            for node in nodes:
                writer.writerow(
                    [node["id"], "|".join(node["labels"]), node["properties"]]
                )
        relationships = session.read_transaction(fetch_relationships)
        with open(
            config["RELATIONSHIPS_CSV_PATH"], "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["rel_id", "start_id", "end_id", "type", "properties"])
            for rel in relationships:
                writer.writerow(
                    [
                        rel["rel_id"],
                        rel["start_id"],
                        rel["end_id"],
                        rel["type"],
                        rel["properties"],
                    ]
                )

    logger.info("CSV files created successfully.")


if __name__ == "__main__":
    generate_data()
    driver.close()
