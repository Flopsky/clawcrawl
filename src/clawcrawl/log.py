"""Logging configuration for clawcrawl."""

import logging

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logging once at application startup."""
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=LOG_FORMAT)
        logging.getLogger(__name__).info("Start setup_logging")
        logging.getLogger(__name__).info("End setup_logging")