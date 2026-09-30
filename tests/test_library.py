"""Unit tests for the Library service."""

import tempfile
import unittest
from datetime import date, timedelta

from services.library import Library
from utils.exceptions import (
    BookNotAvailableError,
    BookNotFoundError,
    DuplicateEntryError,
    InvalidInputError,
    MemberLimitExceededError,
)
from utils.storage import Storage


class TestLibrary(unittest.TestCase):
    def setUp(self):
        # Each test uses its own temporary folder, so real data is untouched.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.library = Library(Storage(self.temp_dir.name))
        self.library.add_book("B1", "Python Basics", "Guido", 1)
        self.library.add_member("M1", "Asha", "asha@x.com", "Student")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_duplicate_book_is_rejected(self):
        with self.assertRaises(DuplicateEntryError):
            self.library.add_book("b1", "Another", "Someone", 1)

    def test_unknown_book_raises_error(self):
        with self.assertRaises(BookNotFoundError):
            self.library.get_book("NOPE")

    def test_issue_and_on_time_return_has_no_fine(self):
        self.library.issue_book("M1", "B1")
        self.assertEqual(self.library.get_book("B1").available_copies, 0)
        transaction = self.library.return_book("M1", "B1")
        self.assertEqual(transaction.fine, 0)
        self.assertEqual(self.library.get_book("B1").available_copies, 1)

    def test_late_return_charges_fine(self):
        # Issued 20 days ago -> due 14 days later -> 6 days late -> Rs. 12.
        issued = date.today() - timedelta(days=20)
        self.library.issue_book("M1", "B1", issue_date=issued)
        transaction = self.library.return_book("M1", "B1")
        self.assertEqual(transaction.days_late(), 6)
        self.assertEqual(transaction.fine, 12)

    def test_no_copies_left(self):
        self.library.add_member("M2", "Ravi", "ravi@x.com", "Student")
        self.library.issue_book("M1", "B1")
        with self.assertRaises(BookNotAvailableError):
            self.library.issue_book("M2", "B1")

    def test_student_cannot_exceed_book_limit(self):
        for number in (2, 3, 4):
            self.library.add_book(f"B{number}", f"Book {number}", "Author", 1)
        for book_id in ("B1", "B2", "B3"):
            self.library.issue_book("M1", book_id)
        with self.assertRaises(MemberLimitExceededError):
            self.library.issue_book("M1", "B4")

    def test_issued_book_cannot_be_deleted(self):
        self.library.issue_book("M1", "B1")
        with self.assertRaises(InvalidInputError):
            self.library.delete_book("B1")

    def test_data_is_saved_and_reloaded(self):
        self.library.issue_book("M1", "B1")
        reloaded = Library(Storage(self.temp_dir.name))
        self.assertEqual(reloaded.get_book("B1").available_copies, 0)
        self.assertEqual(len(reloaded.transactions), 1)


if __name__ == "__main__":
    unittest.main()