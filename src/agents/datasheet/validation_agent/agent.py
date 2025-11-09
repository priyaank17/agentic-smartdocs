"""Validation and sanity checking agent."""

from typing import Any, Dict, List


class ValidationAgent:
    REQUIRED_FIELDS = {"asset_name", "service", "operating_conditions"}

    async def run(self, page_jsons: List[Dict[str, Any] | None]) -> List[Dict[str, Any]]:
        validated = []
        for payload in page_jsons:
            if not isinstance(payload, dict):
                payload = {}
            missing = [field for field in self.REQUIRED_FIELDS if field not in payload]
            for field in missing:
                payload[field] = "UNKNOWN"
            validated.append(payload)
        return validated
