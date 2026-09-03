import logging
import os

from logging.handlers import (
    RotatingFileHandler
)

LOG_FOLDER = "logs"

LOG_FILE = os.path.join(
    LOG_FOLDER,
    "execution.log"
)


def configure_logger():

    os.makedirs(
        LOG_FOLDER,
        exist_ok=True
    )

    logger = logging.getLogger(
        "MDEX"
    )

    logger.propagate = False

    logger.setLevel(
        logging.INFO
    )

    if logger.handlers:

        return logger

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)-8s | "
        "%(message)s"
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setLevel(
        logging.INFO
    )

    file_handler.setFormatter(
        formatter
    )

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        logging.INFO
    )

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )

    return logger