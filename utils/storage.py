"""JSON storage helper for the Library Management System.

Saves and loads lists of records as JSON files. Writes are done safely:
data is first written to a temporary file and then swapped in, and the
previous version is kept as a .bak backup. If a file is corrupted, the
backup is used instead so data is not lost.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

# The "data" folder sits next to main.py, one level above this utils folder.
DEFAULT_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)


class Storage:
    """Reads and writes JSON files inside one data folder."""

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)

    def _path(self, filename):
        """Return the full path of a file inside the data folder."""
        return os.path.join(self.data_dir, filename)

    def load(self, filename):
        """Load a list of records from a JSON file.

        Tries the main file first, then its .bak backup. Returns an empty
        list if the file does not exist yet or cannot be read.
        """
        path = self._path(filename)
        for candidate in (path, path + ".bak"):
            if not os.path.exists(candidate):
                continue
            try:
                with open(candidate, "r", encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, OSError) as error:
                logger.error("Could not read %s: %s", candidate, error)
        return []

    def save(self, filename, records):
        """Save a list of records to a JSON file safely.

        Steps: write to a .tmp file, keep the old file as .bak, then
        replace the main file with the new one.
        """
        path = self._path(filename)
        temp_path = path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=4)
            if os.path.exists(path):
                os.replace(path, path + ".bak")
            os.replace(temp_path, path)
        except OSError as error:
            logger.error("Could not save %s: %s", path, error)
            raise
