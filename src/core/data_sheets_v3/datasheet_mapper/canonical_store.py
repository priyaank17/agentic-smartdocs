""".This module defines a CanonicalStore class that collects canonical JSON incrementally."""
from typing import Dict, Any


class CanonicalStore:
    """
    Holds the progressively-built canonical JSON.

    • ``schema``   –  full JSON-schema dictionary (read-only reference)
    • ``data``     –  dict that grows as the mapper writes values
    """

    def __init__(self, schema: Dict[str, Any]) -> None:
        self.schema: Dict[str, Any] = schema
        self.data: Dict[str, Any] = {}

    # ───────────────────────────────────────────────────────────────
    #  Write helper
    # ───────────────────────────────────────────────────────────────
    def write(self, entity: str, prop: str | None, value: Any) -> None:
        """Write ``value`` into the canonical store.

        • If *entity* isn’t in the schema → append to ``data["others"]``.
        • For array entities, append items.
        • For object entities:
            – known props go to root level
            – unknown props go under ``additional_properties``.
        """
        if entity not in self.schema["properties"]:
            self.data.setdefault("others", []).append(
                {"entity": entity, "prop": prop, "value": value}
            )
            return

        spec = self.schema["properties"][entity]

        # — array entity —
        if spec["type"] == "array":
            target = self.data.setdefault(entity, [])
            item = value if isinstance(value, dict) else {"__value__": value}
            target.append(item)
            return

        # — object entity —
        ent_obj = self.data.setdefault(entity, {})
        if prop in spec.get("properties", {}):
            ent_obj[prop] = value
        else:
            ent_obj.setdefault("additional_properties", {})[prop] = value
