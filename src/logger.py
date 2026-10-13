"""Configuration du logger."""

import logging
import sys
from config.settings import LOG_LEVEL


def get_logger(name: str = "translog") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
    return logger