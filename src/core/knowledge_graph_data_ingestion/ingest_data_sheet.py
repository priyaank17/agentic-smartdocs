"""This module provides functionality to ingest data sheets"""

# pylint: disable=R0801
import time
from src.utils.neo4j_connector import Neo4jConnection
from src.utils.log import logger
from src.constants import ADM_IngestionStatus


def _ingest_subparts(session, data):
    """
    Ingests subpart data into the database and establishes relationships
    between subparts, nozzles, and data sheets.

    Args:
        session: The database session used to run queries.
        data (dict): A dictionary containing the subpart data.

    The function updates the properties of each subpart node in the database,
    ensures the creation of subparts if they do not exist, and establishes
    relationships between subparts, equipment, nozzles, and the corresponding
    data sheet.
    """
    subparts = data["subparts"]
    equipmentTag = data["equipmentTag"]
    dataSheetUuid = data["dataSheetUuid"]
    plantId = data["plantId"]
    for subpart in subparts:
        if "uuid" not in subpart or not subpart["uuid"]:
            logger.info("Skipping subpart")
            continue
        subpartUuid = subpart.get("uuid")
        equipmentUuid = subpart.get("equipmentUuid")
        equipmentTypeName = subpart.get("equipmentTypeName", "")
        properties = {
            "dataSheetUuid": dataSheetUuid,
            "label": "SubPart",
            "equipmentTypeName": equipmentTypeName,
            **{k: v for k, v in subpart.items() if k != "uuid"},
        }
        # MERGE (e)-[:HAS_SUBPART {plantId: $plantId}]->(sp)
        subpart_merge_query = """
        MATCH (e:EQUIPMENT {equipmentUuid: $equipmentUuid, plantId: $plantId})
        MERGE (sp:SUBPART {subpartUuid: $subpartUuid, equipmentTag: $equipmentTag, plantId: $plantId})
        ON CREATE SET sp += $properties, sp.source = "dataSheet"
        ON MATCH SET sp += $properties
        MERGE (e)-[:CONTAINS_SUBPART {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(sp)
        MERGE (sp)-[:PART_OF_EQUIPMENT {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(e)
        RETURN sp
        """

        session.run(
            subpart_merge_query,
            equipmentTag=equipmentTag,
            equipmentUuid=equipmentUuid,
            subpartUuid=subpartUuid,
            properties=properties,
            equipmentTypeName=equipmentTypeName,
            plantId=plantId,
        )
        # MERGE (sp)-[:HAS_NOZZLE {plantId: $plantId}]->(n)
        subpart_to_nozzle_query = """
        MATCH (n:NOZZLE {subpartUuid: $subpartUuid, plantId: $plantId})
        MATCH (sp:SUBPART {subpartUuid: $subpartUuid, plantId: $plantId})
        MERGE (sp)-[:CONTAINS_NOZZLE {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(n)
        MERGE (n)-[:PART_OF_SUBPART {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(sp)

        """
        session.run(
            subpart_to_nozzle_query,
            subpartUuid=subpartUuid,
            plantId=plantId,
            equipmentTypeName=equipmentTypeName,
            equipmentUuid=equipmentUuid,
            equipmentTag=equipmentTag,
        )

        # Link subparts to Data Sheet
        subpart_to_datasheet_query = """
        MATCH (sp:SUBPART {dataSheetUuid: $dataSheetUuid, plantId: $plantId})
        MATCH (d:DATA_SHEET {uuid: $dataSheetUuid, plantId: $plantId})
        MERGE (sp)-[:BELONGS_TO_DATA_SHEET {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(d)
        MERGE (d)-[:DESCRIBES_SUBPART {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(sp)
        """
        session.run(
            subpart_to_datasheet_query,
            dataSheetUuid=dataSheetUuid,
            plantId=plantId,
            equipmentTypeName=equipmentTypeName,
            equipmentUuid=equipmentUuid,
            subpartUuid=subpartUuid,
            equipmentTag=equipmentTag,
        )


def _ingest_nozzles(session, data):
    """
    Ingests nozzle data into the database and establishes relationships
    between nozzles and data sheets.

    Args:
        session: The database session used to run queries.
        data (dict): A dictionary containing the nozzle data.

    The function updates the properties of each nozzle node in the database,
    ensures the creation of nozzles if they do not exist, and establishes
    relationships between nozzles, equipment, and the corresponding data sheet.
    """
    nozzles = data["nozzles"]
    equipmentTag = data["equipmentTag"]
    dataSheetUuid = data["dataSheetUuid"]
    plantId = data["plantId"]
    for nozzle in nozzles:
        if "uuid" not in nozzle or not nozzle["uuid"]:
            logger.info(f"Nozzle UUID is not available. Skipping nozzle: {nozzle}")
            continue

        equipmentUuid = nozzle.get("equipmentUuid", "")
        subpartUuid = nozzle.get("subpartUuid", "")
        nozzleUuid = nozzle.get("uuid", "")
        equipmentTypeName = nozzle.get("equipmentTypeName", "")

        nozzle_properties = {k: v for k, v in nozzle.items() if k != "uuid"}
        nozzle_properties["dataSheetUuid"] = dataSheetUuid

        nozzle_query = """
        MERGE (n:NOZZLE {nozzleUuid: $nozzleUuid})
        ON CREATE SET
            n.equipmentTag = $equipmentTag,
            n.plantId = $plantId,
            n += $nozzle_properties,
            n.source = "dataSheet",
            n.label = "Nozzle",
            n.equipmentTypeName = $equipmentTypeName
        ON MATCH SET
            n += $nozzle_properties
        """
        # MERGE (e)-[:HAS_NOZZLE {plantId: $plantId}]->(n)

        session.run(
            nozzle_query,
            equipmentTag=equipmentTag,
            equipmentUuid=equipmentUuid,
            subpartUuid=subpartUuid,
            nozzleUuid=nozzleUuid,
            nozzle_properties=nozzle_properties,
            equipmentTypeName=equipmentTypeName,
            plantId=plantId,
        )

        create_equipment_nozzle_rels = """
            MATCH (e:EQUIPMENT {equipmentUuid: $equipmentUuid, plantId: $plantId})
            MATCH (n:NOZZLE {nozzleUuid: $nozzleUuid, plantId: $plantId})
            MERGE (e)-[:CONTAINS_NOZZLE {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(n)
            MERGE (n)-[:PART_OF_EQUIPMENT {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(e)
        """

        session.run(
            create_equipment_nozzle_rels,
            equipmentUuid=equipmentUuid,
            nozzleUuid=nozzleUuid,
            equipmentTypeName=equipmentTypeName,
            plantId=plantId,
        )

        nozzle_data_sheet_relationship_query = """
            MATCH (n:NOZZLE {dataSheetUuid: $dataSheetUuid,plantId: $plantId})
            MATCH (d:DATA_SHEET {uuid: $dataSheetUuid,plantId: $plantId})
            MERGE (n)-[r:BELONGS_TO_DATA_SHEET {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(d)
            MERGE (d)-[:DESCRIBES_NOZZLE {plantId: $plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(n)
            ON CREATE SET r.plantId=$plantId
        """
        session.run(
            nozzle_data_sheet_relationship_query,
            dataSheetUuid=dataSheetUuid,
            plantId=plantId,
            equipmentTypeName=equipmentTypeName,
            equipmentUuid=equipmentUuid,
            nozzleUuid=nozzleUuid
        )


def _ingest_equipments(session, data):
    """
    Ingests equipment data into the database and establishes relationships
    between equipments and data sheets.

    Args:
        session: The database session used to run queries.
        data (dict): A dictionary containing the equipment data.

    The function updates the properties of each equipment node in the database
    and establishes a relationship between each equipment and the corresponding
    data sheet.
    """
    equipments = data["equipments"]
    # equipmentTag = data["equipmentTag"]
    dataSheetUuid = data["dataSheetUuid"]
    plantId = data["plantId"]
    for equipment in equipments:
        # properties = {
        #     "dataSheetUuid": data["dataSheetUuid"],
        # }
        equipmentUuid = equipment.get("uuid")
        equipmentTypeName = equipment.get("equipmentTypeName", "")
        properties = {
            "dataSheetUuid": dataSheetUuid,
            "plantId": plantId,
            "label": "Equipment",
            "equipmentTypeName": equipmentTypeName,
            "equipmentUuid": equipmentUuid,
            **{k: v for k, v in equipment.items() if k != "uuid"},
        }
        query = """
            MERGE (e:EQUIPMENT {equipmentUuid: $equipmentUuid})
            ON CREATE SET e += $properties
            ON MATCH SET e += $properties
        """
        session.run(
            query,
            equipmentUuid=equipmentUuid,
            properties=properties,
            plantId=plantId,
        )
        relationship_query = """
            MATCH (e:EQUIPMENT {equipmentUuid: $equipmentUuid, dataSheetUuid: $dataSheetUuid, plantId: $plantId})
            MATCH (d:DATA_SHEET {uuid: $dataSheetUuid, plantId: $plantId})
            MERGE (e)-[:BELONGS_TO_DATA_SHEET {plantId:$plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(d)
            MERGE (d)-[:DESCRIBES_EQUIPMENT {plantId:$plantId, equipmentTypeName: $equipmentTypeName, equipmentUuid: $equipmentUuid}]->(e)
        """
        # session.run(relationship_query, dataSheetUuid=dataSheetUuid, plantId=plantId)
        session.run(
            relationship_query,
            dataSheetUuid=dataSheetUuid,
            plantId=plantId,
            equipmentTypeName=equipmentTypeName,
            equipmentUuid=equipmentUuid,
        )


def _ingest_nodes(session, node_data):
    """This function ingests auxiliary equipment node into the database"""

    properties_list = node_data.get("properties", [])
    label = node_data["label"]
    plantId = node_data["plantId"]
    dataSheetUuid = node_data["dataSheetUuid"]

    if not properties_list:
        raise ValueError("Missing or empty 'properties' in node_data")

    for node_subtype in properties_list:
        print("node_subtype", node_subtype)

        if "uuid" not in node_subtype:
            raise ValueError("Missing 'uuid' in one of the equipment properties")

        equipmentTypeName = node_subtype.get("equipmentTypeName")
        subpartTypeName = node_subtype.get("subpartTypeName")
        node_subtype_uuid = node_subtype["uuid"]
        equipmentUuid = node_subtype.get("equipmentUuid")

        # Build node properties
        properties = {
            "dataSheetUuid": dataSheetUuid,
            "plantId": plantId,
            "label": label,
            "equipmentTypeName": equipmentTypeName,
            "equipmentUuid": equipmentUuid,
            "subpartTypeName": subpartTypeName,
            **{k: v for k, v in node_subtype.items() if k != "uuid"},
        }

        # Create or update the node
        query = f"""
            MERGE (a:{label.upper()} {{uuid: $node_subtype_uuid}})
            ON CREATE SET a += $properties
            ON MATCH SET a += $properties
        """
        session.run(query, node_subtype_uuid=node_subtype_uuid, properties=properties)

        # Dynamically construct relationship properties
        rel_props = """
            plantId: $plantId,
            dataSheetUuid: $dataSheetUuid,
            equipmentTypeName: $equipmentTypeName
        """
        # describes_props = rel_props

        parameters = {
            "dataSheetUuid": dataSheetUuid,
            "equipmentUuid": equipmentUuid,
            "plantId": plantId,
            "equipmentTypeName": equipmentTypeName,
        }

        if subpartTypeName is not None:
            rel_props += ", subpartTypeName: $subpartTypeName"
            # describes_props += ", subpartTypeName: $subpartTypeName"
            parameters["subpartTypeName"] = subpartTypeName

        # Add uuid to match correct node
        parameters["node_subtype_uuid"] = node_subtype_uuid

        relationship_query = f"""
            MATCH (a:{label.upper()} {{uuid: $node_subtype_uuid}})
            MATCH (d:DATA_SHEET {{uuid: $dataSheetUuid, plantId: $plantId}})
            MERGE (a)-[r:BELONGS_TO_DATA_SHEET {{
                {rel_props}
            }}]->(d)
            MERGE (d)-[:DESCRIBES_{label.upper()} {{
                {rel_props}
            }}]->(a)
        """

        session.run(relationship_query, parameters)

        # equipment_relationship_query

        equip_rel_props = """
            plantId: $plantId,
            equipmentUuid: $equipmentUuid,
            equipmentTypeName: $equipmentTypeName
        """

        equipment_relationship_query = f"""
            MATCH (a:{label.upper()} {{uuid: $node_subtype_uuid}})
            MATCH (e:EQUIPMENT {{equipmentUuid: $equipmentUuid, plantId: $plantId}})
            MERGE (a)-[r:PART_OF_EQUIPMENT {{
                {equip_rel_props}
            }}]->(e)
            MERGE (e)-[:CONTAINS_{label.upper()} {{
                {equip_rel_props}
            }}]->(a)
        """

        session.run(equipment_relationship_query, parameters)


def _ingest_data_sheet_node(session, meta_data, plant_id):
    """This function ingests data sheet node into the database"""
    ingestion_start_time = int(time.time() * 1000)
    properties = {
        **meta_data,
        "admIngestionStatus": ADM_IngestionStatus.INGESTING,
        "admIngestionStartingTimestamp": ingestion_start_time,
    }
    query = """
        MERGE(s:DATA_SHEET {uuid: $uuid,plantId: $plantId })
        SET s += $properties
        RETURN s
    """
    session.run(query, properties=properties, uuid=meta_data["uuid"], plantId=plant_id)


def _update_data_sheet_ingestion_timestamp(session, uuid):
    """This function updates the ingestion timestamp of the data sheet"""
    ingestion_end_time = int(time.time() * 1000)
    params = {
        "uuid": uuid,
        "admIngestionStatus": ADM_IngestionStatus.INGESTION_COMPLETED,
        "admIngestionEndingTimestamp": ingestion_end_time,
    }

    query = """
        MATCH(d: DATA_SHEET {uuid: $uuid})
        SET d += $params
    """
    session.run(
        query,
        uuid=uuid,
        params=params,
    )


async def ingest_data_sheet(adm, database_name, plant_id):
    """This function ingests data sheet into the database"""
    logger.info("INIT: ingest_data_sheet")
    neo4j_conn = Neo4jConnection(database_name)
    neo4j_conn.connect()
    equipments = adm.get("equipments")
    nozzles = adm.get("nozzles")
    sub_parts = adm.get("subparts")
    equipmentTag = adm["metaData"]["equipmentTag"]
    dataSheetUuid = adm["metaData"]["uuid"]
    logger.info(f"Ingesting DATA_SHEET node: {equipmentTag}")
    logger.info("Ingesting metadata...")
    neo4j_conn.execute_write(_ingest_data_sheet_node, adm["metaData"], plant_id)

    logger.info("Ingesting equipment(s): %s", equipmentTag)
    equipment_data = {
        "equipments": equipments,
        "equipmentTag": equipmentTag,
        "dataSheetUuid": dataSheetUuid,
        "plantId": plant_id,
    }
    neo4j_conn.execute_write(_ingest_equipments, equipment_data)

    if nozzles:
        logger.info("Ingesting Nozzles...")
        nozzle_data = {
            "nozzles": nozzles,
            "equipmentTag": equipmentTag,
            "dataSheetUuid": dataSheetUuid,
            "plantId": plant_id,
        }
        neo4j_conn.execute_write(_ingest_nozzles, nozzle_data)
    else:
        logger.info("No nozzles to ingest.")

    if sub_parts:
        logger.info("Ingesting subparts...")
        sub_parts_data = {
            "subparts": sub_parts,
            "equipmentTag": equipmentTag,
            "dataSheetUuid": dataSheetUuid,
            "plantId": plant_id,
            "label": "SubPart",
        }
        neo4j_conn.execute_write(_ingest_subparts, sub_parts_data)
    else:
        logger.info("No subparts to ingest.")

    for node in adm:
        if node not in ["metaData", "equipments", "nozzles", "subparts"]:
            logger.info(f"Ingesting {node}...")
            node_data = {
                "properties": adm[node],
                "dataSheetUuid": dataSheetUuid,
                "plantId": plant_id,
                "label": node,
            }
            # neo4j_conn.execute_write(_ingest_nodes, node_data)
            neo4j_conn.execute_write(
                _ingest_nodes,
                node_data,
            )

    logger.info("Finishing Ingestion of Data Sheet...")
    neo4j_conn.execute_write(_update_data_sheet_ingestion_timestamp, dataSheetUuid)
    logger.info("INIT: ingest_data_sheet")
