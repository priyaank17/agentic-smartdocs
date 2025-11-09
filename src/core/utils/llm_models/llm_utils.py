"""This module contains utility functions for LLM models."""

import time
from openai import RateLimitError
from src.utils.log import logger


TOKEN_LIMIT_PER_SECOND = 1000  # Replace with your actual token rate limit
MAX_RETRIES = 5  # Maximum number of retries for rate limit errors
RETRY_BACKOFF_BASE = 2  # Base for exponential backoff


# def throttle_request(last_request_time):
#     """Throttle API requests based on token rate limit."""
#     now = time.time()
#     logger.info(f"Time since last request: {now - last_request_time}")
#     elapsed = now - last_request_time
#     print("Requests per second:", elapsed, TOKEN_LIMIT_PER_SECOND)
#     if elapsed < 1 / TOKEN_LIMIT_PER_SECOND:
#         time.sleep((1 / TOKEN_LIMIT_PER_SECOND) - elapsed)
#     return time.time()


def retry_with_backoff(func, *args, table_name=None, **kwargs):
    """Retry logic for handling rate limits."""
    retries = 0
    logger.info("Starting API call")
    while retries < MAX_RETRIES:
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            retries += 1
            if 'Please retry after' in str(e):
                wait_time = 30
            else:
                wait_time = RETRY_BACKOFF_BASE**retries
            logger.warning(
                f'''Rate limit exceeded. Retrying in {wait_time} seconds...
                for {table_name} (Attempt {retries}/{MAX_RETRIES})'''
            )
            time.sleep(wait_time)
    logger.error("Max retries reached. Rate limit issue persists.")
    raise RateLimitException("Max retries reached. Rate limit issue persists.")


class RateLimitException(Exception):
    """Custom exception for rate limit issues."""
