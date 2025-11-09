"""This module contains utility functions"""

import json

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
}


def get_return_type(is_api_event=False, data=None):
    """
    Prepares the return type based on the context.
    If is_context is True, it wraps the data in an HTTP response format.
    Otherwise, it returns the raw data.
    """
    if is_api_event:
        return {"headers": HEADERS, "statusCode": 200, "body": json.dumps(data)}
    return data
