"""Custom exceptions for the Library Management System.

Using specific exceptions (instead of generic ones) lets the rest of the
program handle each error case clearly and show friendly messages.
"""


class LibraryError(Exception):
    """Base class for all library-related errors."""


class BookNotFoundError(LibraryError):
    """Raised when a book ID does not exist."""


class MemberNotFoundError(LibraryError):
    """Raised when a member ID does not exist."""


class BookNotAvailableError(LibraryError):
    """Raised when no copies of a book are left to issue."""


class MemberLimitExceededError(LibraryError):
    """Raised when a member tries to borrow more books than allowed."""


class DuplicateEntryError(LibraryError):
    """Raised when adding a book or member whose ID already exists."""


class InvalidInputError(LibraryError):
    """Raised when user input fails validation."""


class AuthenticationError(LibraryError):
    """Raised when a librarian login fails."""