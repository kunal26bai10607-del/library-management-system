"""Member models for the Library Management System.

Member is the base class. StudentMember and FacultyMember inherit from it
and override the rules (book limit, loan period, fine rate). This is an
example of inheritance and polymorphism.
"""

from utils.exceptions import InvalidInputError, MemberLimitExceededError


class Member:
    """Base class for all library members."""

    member_type = "Member"
    max_books = 3       # maximum books a member can hold at once
    loan_days = 14      # days before a book is due
    fine_per_day = 2    # fine (in rupees) for each late day

    def __init__(self, member_id, name, email, borrowed_books=None):
        if not str(member_id).strip():
            raise InvalidInputError("Member ID cannot be empty.")
        if not str(name).strip():
            raise InvalidInputError("Name cannot be empty.")
        if "@" not in str(email) or "." not in str(email):
            raise InvalidInputError("Please enter a valid email address.")

        self.member_id = str(member_id).strip().upper()
        self.name = str(name).strip()
        self.email = str(email).strip()
        # Stores the IDs of books currently borrowed by this member.
        self.borrowed_books = list(borrowed_books) if borrowed_books else []

    def can_borrow(self):
        """Return True if the member has not reached their book limit."""
        return len(self.borrowed_books) < self.max_books

    def borrow(self, book_id):
        """Record that this member has borrowed a book."""
        if not self.can_borrow():
            raise MemberLimitExceededError(
                f"{self.name} has already borrowed {self.max_books} books."
            )
        if book_id in self.borrowed_books:
            raise InvalidInputError("This member already has this book.")
        self.borrowed_books.append(book_id)

    def return_book(self, book_id):
        """Record that this member has returned a book."""
        if book_id not in self.borrowed_books:
            raise InvalidInputError("This member has not borrowed that book.")
        self.borrowed_books.remove(book_id)

    def calculate_fine(self, days_late):
        """Return the fine for a book returned days_late days after the due date."""
        if days_late <= 0:
            return 0
        return days_late * self.fine_per_day

    def to_dict(self):
        """Convert the member to a dictionary so it can be saved as JSON."""
        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "member_type": self.member_type,
            "borrowed_books": self.borrowed_books,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild the correct member type (Student/Faculty) from JSON data."""
        member_class = MEMBER_TYPES.get(data.get("member_type"), StudentMember)
        return member_class(
            data["member_id"],
            data["name"],
            data["email"],
            data.get("borrowed_books", []),
        )

    def __str__(self):
        return (
            f"[{self.member_id}] {self.name} ({self.member_type}) - "
            f"{len(self.borrowed_books)}/{self.max_books} books borrowed"
        )


class StudentMember(Member):
    """Students: 3 books, 14 days, Rs. 2 fine per late day."""

    member_type = "Student"
    max_books = 3
    loan_days = 14
    fine_per_day = 2


class FacultyMember(Member):
    """Faculty: 5 books, 30 days, Rs. 1 fine per late day."""

    member_type = "Faculty"
    max_books = 5
    loan_days = 30
    fine_per_day = 1


# Lets from_dict() pick the right class from the saved member_type text.
MEMBER_TYPES = {
    "Student": StudentMember,
    "Faculty": FacultyMember,
}