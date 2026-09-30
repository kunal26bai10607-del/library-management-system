"""Librarian login for the Library Management System.

Passwords are never stored as plain text. Each password is combined with
a random salt and hashed with PBKDF2-SHA256 before being saved.
"""

import hashlib
import hmac
import logging
import os

from utils.exceptions import AuthenticationError, InvalidInputError
from utils.storage import Storage

logger = logging.getLogger(__name__)

USERS_FILE = "users.json"
HASH_ROUNDS = 100_000
MIN_PASSWORD_LENGTH = 6

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"


def hash_password(password, salt=None):
    """Return (salt_hex, hash_hex) for the given password."""
    salt_bytes = bytes.fromhex(salt) if salt else os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt_bytes, HASH_ROUNDS
    )
    return salt_bytes.hex(), digest.hex()


class AuthService:
    """Creates librarian accounts and checks logins."""

    def __init__(self, storage=None):
        self.storage = storage or Storage()
        self.users = self.storage.load(USERS_FILE)
        if not self.users:
            # First run: create a default account so the librarian can log in.
            self.add_user(DEFAULT_USERNAME, DEFAULT_PASSWORD)
            logger.info("Created default librarian account.")

    def _find_user(self, username):
        """Return the saved user record, or None."""
        for user in self.users:
            if user["username"] == username:
                return user
        return None

    def add_user(self, username, password):
        """Create a new librarian account."""
        username = str(username).strip().lower()
        if not username:
            raise InvalidInputError("Username cannot be empty.")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidInputError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
            )
        if self._find_user(username):
            raise InvalidInputError("That username already exists.")

        salt, hashed = hash_password(password)
        self.users.append({"username": username, "salt": salt, "hash": hashed})
        self.storage.save(USERS_FILE, self.users)
        logger.info("Created librarian account '%s'.", username)

    def login(self, username, password):
        """Return True if the login is correct; otherwise raise an error."""
        user = self._find_user(str(username).strip().lower())
        if user is None:
            logger.warning("Failed login: unknown user '%s'.", username)
            raise AuthenticationError("Incorrect username or password.")

        _, attempt = hash_password(password, user["salt"])
        if not hmac.compare_digest(attempt, user["hash"]):
            logger.warning("Failed login for '%s'.", username)
            raise AuthenticationError("Incorrect username or password.")

        logger.info("Librarian '%s' logged in.", user["username"])
        return True