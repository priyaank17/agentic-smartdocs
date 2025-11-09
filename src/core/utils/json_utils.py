"""Utility functions for JSON operations."""

import json
import re
from src.utils.log import logger


def extract_json_from_text(text):
    """Extract JSON from a given text."""
    # json_match = re.search(r'\[\s*{.*?}\s*\]', text, re.DOTALL)
    json_match = re.search(r"\[.*\]", text, re.DOTALL)

    if json_match:
        json_string = json_match.group(0)
        try:
            data = json.loads(json_string)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return None
    else:
        logger.error("No JSON found in the text.")
        return None
