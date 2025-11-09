"""Get response from Junior API."""

from src.utils.log import logger


def load_junior_input(file_path, **kwargs):
    """Load API input from a Markdown file and format it with dynamic values."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = "".join(
                line for line in file if not line.strip().startswith("#")
            ).strip()
            return content.format(**kwargs)
    except FileNotFoundError:
        logger.error(f"Markdown file not found at path: {file_path}")
    except KeyError as e:
        logger.error(f"Missing key for formatting: {e}")
    return None
