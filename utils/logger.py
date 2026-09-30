"""Logging setup for the Library Management System.

Every action (add, issue, return, errors) is written to library.log so
there is a record of what happened and when.
"""

import logging
import os

LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "library.log"
)


def setup_logging(log_file=LOG_FILE):
    """Send log messages to a file with the date, time and severity."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        encoding="utf-8",
    )