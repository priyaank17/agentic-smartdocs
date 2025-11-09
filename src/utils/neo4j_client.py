"""Shared Neo4j connector utilities."""

from contextlib import contextmanager
from typing import Any, Dict, List

from neo4j import GraphDatabase

from src.config.settings import get_settings

settings = get_settings()

_driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
)


@contextmanager
def neo4j_session(database: str | None = None):
    session = _driver.session(database=database)
    try:
        yield session
    finally:
        session.close()


def _sanitize_label(label: str) -> str:
    cleaned = "".join(ch for ch in (label or "Node") if ch.isalnum() or ch in "_")
    return cleaned or "Node"


def _merge_nodes(session, nodes: List[Dict[str, Any]]):
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            continue
        label = _sanitize_label(node.get("label", "Asset"))
        props = {k: v for k, v in node.items() if k not in {"label"}}
        session.run(
            f"MERGE (n:`{label}` {{id: $id}}) SET n += $props",
            id=node_id,
            props=props,
        )


def _merge_relationships(session, rels: List[Dict[str, Any]]):
    for rel in rels:
        start = rel.get("start")
        end = rel.get("end")
        if not start or not end:
            continue
        rel_type = _sanitize_label(rel.get("type", "RELATED_TO"))
        props = {k: v for k, v in rel.items() if k not in {"start", "end", "type"}}
        session.run(
            f"MATCH (s {{id: $start_id}}), (e {{id: $end_id}}) "
            f"MERGE (s)-[r:`{rel_type}`]->(e) SET r += $props",
            start_id=start,
            end_id=end,
            props=props,
        )


async def ingest_adm(adm: Dict[str, Any], database: str | None = None) -> Dict[str, Any]:
    """Persist graph payload (nodes + relationships) into Neo4j."""
    nodes = adm.get("nodes", []) if isinstance(adm, dict) else []
    rels = adm.get("relationships", []) if isinstance(adm, dict) else []

    def _run_transaction(nodes_payload: List[Dict[str, Any]], rel_payload: List[Dict[str, Any]]):
        with neo4j_session(database) as session:
            _merge_nodes(session, nodes_payload)
            _merge_relationships(session, rel_payload)
        return {
            "nodes_ingested": len(nodes_payload),
            "relationships_ingested": len(rel_payload),
        }

    from anyio.to_thread import run_sync

    return await run_sync(_run_transaction, nodes, rels)
