"""This module contains the Neo4jConnection class to connect to the Neo4j database."""

import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable, Neo4jError
from src.utils.log import logger
from src.graphql.utils import call_graph_ql
from src.graphql.operations import GET_DATABASE_NAME_FROM_PLANT_ID


async def get_database_name(plant_id):
    """Function to get database name"""
    variables = json.dumps({"id": plant_id})
    is_running_env_local = os.getenv("LOCAL", default="false")
    database_name = ""
    if is_running_env_local == "true":
        database_name = "db" + plant_id.replace("-", "")
    else:
        res = call_graph_ql(
            query=GET_DATABASE_NAME_FROM_PLANT_ID,
            operation_name="GET_DATABASE_NAME_FROM_PLANT_ID",
            operation_type="query",
            variables=variables,
        )
        database_name = res["data"]["getPlant"]["graphDatabaseUniqueId"]
    return database_name


class Neo4jConnection:
    """Neo4jConnection class to connect to the Neo4j database."""

    def __init__(self, database_name):
        load_dotenv()
        self.uri = os.getenv("NEO4J_URI", "")
        self.username = os.getenv("NEO4J_USERNAME", "")
        self.password = os.getenv("NEO4J_PASSWORD", "")
        self.driver = None
        self.database_name = database_name

    def connect(self):
        """Connect to the Neo4j database."""

        if not self.driver:
            try:
                logger.info(
                    "INIT: Creating database connection : %s", self.database_name
                )
                self.username = os.getenv("NEO4J_USERNAME", "")
                self.password = os.getenv("NEO4J_PASSWORD", "")
                self.driver = GraphDatabase.driver(
                    uri=self.uri,
                    auth=(self.username, self.password),
                    max_connection_lifetime=60 * 60 * 1000,
                    max_connection_pool_size=1,
                    encrypted=False,
                )
            except AuthError as e:
                logger.error(f"Authentication failed: {e}")
            except ServiceUnavailable as e:
                logger.error(f"Service unavailable: {e}")
            except Neo4jError as e:  # Catch specific Neo4j error
                logger.error(f"Neo4j error: {e}")
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(f"Unexpected error: {e}")

    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            self.driver = None

    def execute_write(self, query_function, *args):
        """Execute write operations safely."""
        with self.driver.session(database=self.database_name) as session:
            result = session.write_transaction(query_function, *args)
        return result

    @staticmethod
    async def get_database_name(plant_id):
        """Get the database name for the given plant ID."""
        database_name = await get_database_name(plant_id)
        return database_name
