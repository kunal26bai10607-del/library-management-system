"""Transaction model: records one book issue (and its return) for a member."""

from datetime import date, datetime

DATE_FORMAT = "%Y-%m-%d"


class Transaction:
    """One borrowing record: who borrowed which book, and when."""

    def __init__(self, transaction_id, book_id, member_id,
                 issue_date, due_date, return_date=None, fine=0):
        self.transaction_id = transaction_id
        self.book_id = book_id
        self.member_id = member_id
        self.issue_date = issue_date      # datetime.date
        self.due_date = due_date          # datetime.date
        self.return_date = return_date    # datetime.date or None
        self.fine = fine

    def is_returned(self):
        """Return True if the book has already been returned."""
        return self.return_date is not None

    def days_late(self, on_date=None):
        """Number of days past the due date (0 if not late).

        For an unreturned book, compares against today (or on_date).
        For a returned book, compares against the actual return date.
        """
        compare_date = self.return_date or on_date or date.today()
        late = (compare_date - self.due_date).days
        return late if late > 0 else 0

    def is_overdue(self, on_date=None):
        """Return True if the book is not returned and past its due date."""
        return not self.is_returned() and self.days_late(on_date) > 0

    def to_dict(self):
        """Convert to a dictionary for JSON storage (dates become text)."""
        return {
            "transaction_id": self.transaction_id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "issue_date": self.issue_date.strftime(DATE_FORMAT),
            "due_date": self.due_date.strftime(DATE_FORMAT),
            "return_date": (
                self.return_date.strftime(DATE_FORMAT)
                if self.return_date else None
            ),
            "fine": self.fine,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Transaction from a dictionary loaded from JSON."""
        def parse(text):
            return datetime.strptime(text, DATE_FORMAT).date() if text else None

        return cls(
            data["transaction_id"],
            data["book_id"],
            data["member_id"],
            parse(data["issue_date"]),
            parse(data["due_date"]),
            parse(data.get("return_date")),
            data.get("fine", 0),
        )

    def __str__(self):
        status = (
            f"returned {self.return_date}" if self.is_returned()
            else f"due {self.due_date}"
        )
        return (
            f"#{self.transaction_id}: book {self.book_id} -> "
            f"member {self.member_id} ({status}, fine Rs. {self.fine})"
        )