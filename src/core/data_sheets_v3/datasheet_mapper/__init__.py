"""."""
import logging

# Global log level for your app
logging.basicConfig(
    level=logging.INFO,           # <- you see INFO & above
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

# Silence noisy third-party loggers
for noisy in ("httpx", "openai", "langchain"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
