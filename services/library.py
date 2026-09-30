"""Core business logic for the Library Management System.

The Library class ties together books, members and transactions. It
validates input, enforces the borrowing rules, calculates fines, saves
data to JSON files and writes log messages.
"""

import logging
from datetime import date, timedelta

from models.book import Book
from models.member import MEMBER_TYPES
from models.transaction import Transaction
from utils.exceptions import (
    BookNotAvailableError,
    BookNotFoundError,
    DuplicateEntryError,
    InvalidInputError,
    LibraryError,
    MemberNotFoundError,
)
from utils.storage import Storage
from utils.validators import (
    validate_email,
    validate_id,
    validate_non_empty,
    validate_positive_int,
)

logger = logging.getLogger(__name__)

BOOKS_FILE = "books.json"
MEMBERS_FILE = "members.json"
TRANSACTIONS_FILE = "transactions.json"

# Errors that can happen when a saved record is damaged or incomplete.
RECORD_ERRORS = (KeyError, TypeError, ValueError, LibraryError)


class Library:
    """Manages books, members, and issue/return transactions."""

    def __init__(self, storage=None):
        self.storage = storage or Storage()
        self.books = {}          # book_id -> Book
        self.members = {}        # member_id -> Member
        self.transactions = []   # list of Transaction
        self._load()

    # ------------------------------------------------------------------
    # Loading and saving
    # ------------------------------------------------------------------
    def _load(self):
        """Load all saved data, skipping any damaged records."""
        for record in self.storage.load(BOOKS_FILE):
            try:
                book = Book.from_dict(record)
                self.books[book.book_id] = book
            except RECORD_ERRORS as error:
                logger.warning("Skipped a damaged book record: %s", error)

        from models.member import Member  # local import keeps top clean
        for record in self.storage.load(MEMBERS_FILE):
            try:
                member = Member.from_dict(record)
                self.members[member.member_id] = member
            except RECORD_ERRORS as error:
                logger.warning("Skipped a damaged member record: %s", error)

        for record in self.storage.load(TRANSACTIONS_FILE):
            try:
                self.transactions.append(Transaction.from_dict(record))
            except RECORD_ERRORS as error:
                logger.warning("Skipped a damaged transaction: %s", error)

        logger.info(
            "Loaded %d books, %d members, %d transactions.",
            len(self.books), len(self.members), len(self.transactions),
        )

    def _save(self):
        """Save books, members and transactions to their JSON files."""
        self.storage.save(BOOKS_FILE, [b.to_dict() for b in self.books.values()])
        self.storage.save(
            MEMBERS_FILE, [m.to_dict() for m in self.members.values()]
        )
        self.storage.save(
            TRANSACTIONS_FILE, [t.to_dict() for t in self.transactions]
        )

    # ------------------------------------------------------------------
    # Book management
    # ------------------------------------------------------------------
    def add_book(self, book_id, title, author, copies=1):
        """Add a new book to the library."""
        book_id = validate_id(book_id, "Book ID")
        if book_id in self.books:
            raise DuplicateEntryError(f"Book ID {book_id} already exists.")
        title = validate_non_empty(title, "Title")
        author = validate_non_empty(author, "Author")
        copies = validate_positive_int(copies, "Number of copies")

        book = Book(book_id, title, author, copies)
        self.books[book.book_id] = book
        self._save()
        logger.info("Added book %s (%s).", book.book_id, book.title)
        return book

    def get_book(self, book_id):
        """Return a book by ID or raise BookNotFoundError."""
        key = str(book_id).strip().upper()
        if key not in self.books:
            raise BookNotFoundError(f"No book found with ID {key}.")
        return self.books[key]

    def update_book(self, book_id, title=None, author=None, total_copies=None):
        """Change a book's title, author or total number of copies."""
        book = self.get_book(book_id)

        # Validate everything first so a bad value changes nothing.
        new_title = validate_non_empty(title, "Title") if title else None
        new_author = validate_non_empty(author, "Author") if author else None
        new_total = None
        if total_copies not in (None, ""):
            new_total = validate_positive_int(total_copies, "Number of copies")
            issued = book.total_copies - book.available_copies
            if new_total < issued:
                raise InvalidInputError(
                    f"{issued} copies are currently issued, so total copies "
                    f"cannot be less than {issued}."
                )

        if new_title:
            book.title = new_title
        if new_author:
            book.author = new_author
        if new_total is not None:
            issued = book.total_copies - book.available_copies
            book.total_copies = new_total
            book.available_copies = new_total - issued

        self._save()
        logger.info("Updated book %s.", book.book_id)
        return book

    def delete_book(self, book_id):
        """Delete a book, unless some copies are currently issued."""
        book = self.get_book(book_id)
        if book.available_copies != book.total_copies:
            raise InvalidInputError(
                "This book cannot be deleted while copies are issued."
            )
        del self.books[book.book_id]
        self._save()
        logger.info("Deleted book %s.", book.book_id)

    def search_books(self, keyword):
        """Find books whose ID, title or author contains the keyword."""
        keyword = validate_non_empty(keyword, "Search keyword").lower()
        return [
            book for book in self.books.values()
            if keyword in book.book_id.lower()
            or keyword in book.title.lower()
            or keyword in book.author.lower()
        ]

    def list_books(self):
        """Return all books sorted by ID."""
        return sorted(self.books.values(), key=lambda b: b.book_id)

    # ------------------------------------------------------------------
    # Member management
    # ------------------------------------------------------------------
    def add_member(self, member_id, name, email, member_type="Student"):
        """Register a new Student or Faculty member."""
        member_id = validate_id(member_id, "Member ID")
        if member_id in self.members:
            raise DuplicateEntryError(f"Member ID {member_id} already exists.")
        name = validate_non_empty(name, "Name")
        email = validate_email(email)

        member_class = MEMBER_TYPES.get(str(member_type).strip().capitalize())
        if member_class is None:
            raise InvalidInputError("Member type must be Student or Faculty.")

        member = member_class(member_id, name, email)
        self.members[member.member_id] = member
        self._save()
        logger.info("Added member %s (%s).", member.member_id, member.member_type)
        return member

    def get_member(self, member_id):
        """Return a member by ID or raise MemberNotFoundError."""
        key = str(member_id).strip().upper()
        if key not in self.members:
            raise MemberNotFoundError(f"No member found with ID {key}.")
        return self.members[key]

    def update_member(self, member_id, name=None, email=None):
        """Change a member's name or email."""
        member = self.get_member(member_id)
        new_name = validate_non_empty(name, "Name") if name else None
        new_email = validate_email(email) if email else None

        if new_name:
            member.name = new_name
        if new_email:
            member.email = new_email

        self._save()
        logger.info("Updated member %s.", member.member_id)
        return member

    def delete_member(self, member_id):
        """Delete a member, unless they still hold borrowed books."""
        member = self.get_member(member_id)
        if member.borrowed_books:
            raise InvalidInputError(
                "This member still has borrowed books and cannot be deleted."
            )
        del self.members[member.member_id]
        self._save()
        logger.info("Deleted member %s.", member.member_id)

    def list_members(self):
        """Return all members sorted by ID."""
        return sorted(self.members.values(), key=lambda m: m.member_id)

    # ------------------------------------------------------------------
    # Issue and return
    # ------------------------------------------------------------------
    def _next_transaction_id(self):
        """Return the next unused transaction number."""
        return max((t.transaction_id for t in self.transactions), default=0) + 1

    def