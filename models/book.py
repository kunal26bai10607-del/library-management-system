"""Book model for the Library Management System."""

from utils.exceptions import InvalidInputError


class Book:
    """Represents a book and tracks how many copies are available."""

    def __init__(self, book_id, title, author, total_copies=1, available_copies=None):
        if not str(book_id).strip():
            raise InvalidInputError("Book ID cannot be empty.")
        if not str(title).strip():
            raise InvalidInputError("Title cannot be empty.")
        if not str(author).strip():
            raise InvalidInputError("Author cannot be empty.")
        if total_copies < 1:
            raise InvalidInputError("A book must have at least 1 copy.")

        self.book_id = str(book_id).strip().upper()
        self.title = str(title).strip()
        self.author = str(author).strip()
        self.total_copies = total_copies
        # When a new book is added, all copies are available.
        self.available_copies = (
            total_copies if available_copies is None else available_copies
        )

    def is_available(self):
        """Return True if at least one copy can be issued."""
        return self.available_copies > 0

    def issue_copy(self):
        """Reduce available copies by one when the book is issued."""
        self.available_copies -= 1

    def return_copy(self):
        """Increase available copies by one when the book is returned."""
        if self.available_copies < self.total_copies:
            self.available_copies += 1

    def to_dict(self):
        """Convert the book to a dictionary so it can be saved as JSON."""
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Book object from a dictionary loaded from JSON."""
        return cls(
            data["book_id"],
            data["title"],
            data["author"],
            data["total_copies"],
            data["available_copies"],
        )

    def __str__(self):
        return (
            f"[{self.book_id}] {self.title} by {self.author} "
            f"({self.available_copies}/{self.total_copies} available)"
        )