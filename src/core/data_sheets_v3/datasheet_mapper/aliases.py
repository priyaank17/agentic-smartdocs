"""."""
import re
from typing import Dict, Tuple


_CLEAN = lambda s: re.sub(r"[^A-Z0-9]", "", s.upper())  # NOQA


def build_aliases(schema: dict) -> tuple[Dict[str, str], Dict[str, Tuple[str, str]]]:
    """Build entity and property aliases from the schema."""
    ent_alias: Dict[str, str] = {}
    prop_alias: Dict[str, Tuple[str, str]] = {}
    for ent, es in schema["properties"].items():
        for ali in es.get("aliases", []):
            ent_alias[_CLEAN(ali)] = ent
        for prop, ps in es.get("properties", {}).items():
            for ali in ps.get("aliases", []):
                prop_alias[_CLEAN(ali)] = (ent, prop)
    return ent_alias, prop_alias
