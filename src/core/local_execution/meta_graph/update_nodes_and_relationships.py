"""Update the node labels and relationship types in the Neo4j database."""

import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from src.local_execution.meta_graph.get_nodes_and_relationships import generate_data
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
    NODES_CONFIG_PATH = os.path.join(  # pylint: disable=invalid-name
        ROOT_FOLDER_PATH, config["nodes_config_path"]
    )
    config["NODES_CONFIG_PATH"] = NODES_CONFIG_PATH
    RELATIONSHIPS_CONFIG_PATH = os.path.join(  # pylint: disable=invalid-name
        ROOT_FOLDER_PATH, config["relationships_config_path"]
    )
    config["RELATIONSHIPS_CONFIG_PATH"] = RELATIONSHIPS_CONFIG_PATH
    return config


def update_node_labels(tx, configs):
    """Update node labels in the Neo4j database."""
    for old_label, new_label in configs.items():
        query = f"""
        MATCH (n:`{old_label}`)
        REMOVE n:`{old_label}`
        SET n:`{new_label}`
        """
        tx.run(query)
        logger.info(f"Updated node label from {old_label} to {new_label}.")


def update_relationship_types(tx, config):
    """Update relationship types in the Neo4j database."""
    for old_type, new_type in config.items():
        query = f"""
        MATCH ()-[r:`{old_type}`]->()
        CALL apoc.refactor.setType(r, '{new_type}')
        YIELD input, output
        RETURN input, output
        """
        tx.run(query)
        logger.info(f"Updated relationship type from {old_type} to {new_type}.")


def update_graph():
    """Update the graph with the new node labels and relationship types."""
    with driver.session() as session:
        config = _setup_config()
        nodes_config = config["NODES_CONFIG_PATH"]
        relationships_config = config["RELATIONSHIPS_CONFIG_PATH"]
        with open(nodes_config, "r", encoding="utf-8") as f:
            nodes_config = json.load(f)
        with open(relationships_config, "r", encoding="utf-8") as f:
            relationships_config = json.load(f)
        session.write_transaction(update_node_labels, nodes_config)
        session.write_transaction(update_relationship_types, relationships_config)

    logger.info("Graph has been updated successfully.")


if __name__ == "__main__":
    update_graph()
    generate_data()
    driver.close()
