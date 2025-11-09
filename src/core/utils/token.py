"""To handle auth token from the frontend"""
import os
import threading
from src.utils.log import logger

token_storage = threading.local()


def set_token(token):
    "Set the auth token"
    logger.info("Setting token")
    token_storage.token = token


def get_token():
    "Get the auth token"
    token = getattr(token_storage, "token", None)
    logger.info("Getting token")

    return token or os.getenv("ARTISAN_AUTH_TOKEN", "")
