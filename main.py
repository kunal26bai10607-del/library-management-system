"""Library Management System: menu-driven program.

Run with:  py main.py
"""

import getpass
import logging

from services.auth import AuthService
from services.library import Library
from services.report import ReportService, format_table
from utils.exceptions import AuthenticationError, LibraryError
from utils.logger import setup_logging

logger = logging.getLogger(__name__)
MAX_LOGIN_ATTEMPTS = 3


def ask(prompt):
    return input(prompt).strip()


def show(lines):
    print()
    for line in lines:
        print(line)
    print()


# ----------------------------------------------------------------------
# Menu actions. Each one takes the library and the report service.
# ----------------------------------------------------------------------
def add_book(lib, rep):
    book = lib.add_book(
        ask("Book ID: "), ask("Title: "), ask("Author: "),
        ask("Copies [1]: ") or 1,
    )
    print(f"Added '{book.title}'.")


def update_book(lib, rep):
    book = lib.update_book(
        ask("Book ID: "),
        title=ask("New title (Enter to keep): "),
        author=ask("New author (Enter to keep): "),
        total_copies=ask("New total copies (Enter to keep): "),
    )
    print(f"Updated '{book.title}'.")


def delete_book(lib, rep):
    lib.delete_book(ask("Book ID to delete: "))
    print("Book deleted.")


def search_books(lib, rep):
    found = lib.search_books(ask("Search (ID, title or author): "))
    if not found:
        print("No matching books.")
        return
    rows = [
        (b.book_id, b.title, b.author, b.available_copies, b.total_copies)
        for b in found
    ]
    show(format_table(["ID", "Title", "Author", "Available", "Total"], rows))


def add_member(lib, rep):
    member = lib.add_member(
        ask("Member ID: "), ask("Name: "), ask("Email: "),
        ask("Type (Student/Faculty) [Student]: ") or "Student",
    )
    print(f"Added {member.member_type} '{member.name}'.")


def update_member(lib, rep):
    member = lib.update_member(
        ask("Member ID: "),
        name=ask("New name (Enter to keep): "),
        email=ask("New email (Enter to keep): "),
    )
    print(f"Updated '{member.name}'.")


def delete_member(lib, rep):
    lib.delete_member(ask("Member ID to delete: "))
    print("Member deleted.")


def issue_book(lib, rep):
    transaction = lib.issue_book(ask("Member ID: "), ask("Book ID: "))
    print(f"Issued. Due date: {transaction.due_date}")


def return_book(lib, rep):
    transaction = lib.return_book(ask("Member ID: "), ask("Book ID: "))
    print(f"Returned. Fine: Rs. {transaction.fine}")


def show_books(lib, rep):
    show(rep.books_report())


def show_members(lib, rep):
    show(rep.members_report())


def show_overdue(lib, rep):
    show(rep.overdue_report())


def show_history(lib, rep):
    show(rep.member_history_report(ask("Member ID: ")))


def show_summary(lib, rep):
    show(rep.summary_report())


MENU = [
    ("Add book", add_book),
    ("Update book", update_book),
    ("Delete book", delete_book),
    ("Search books", search_books),
    ("Add member", add_member),
    ("Update member", update_member),
    ("Delete member", delete_member),
    ("Issue book", issue_book),
    ("Return book", return_book),
    ("Report: all books", show_books),
    ("Report: all members", show_members),
    ("Report: overdue books", show_overdue),
    ("Report: member history", show_history),
    ("Report: summary", show_summary),
]


def login(auth):
    """Give the librarian a few tries to log in."""
    for _ in range(MAX_LOGIN_ATTEMPTS):
        username = ask("Username: ")
        password = getpass.getpass("Password: ")
        try:
            auth.login(username, password)
            return True
        except AuthenticationError as error:
            print(error)
    print("Too many failed attempts.")
    return False


def print_menu():
    print("\n=== Library Management System ===")
    for number, (label, _) in enumerate(MENU, start=1):
        print(f"{number:>2}. {label}")
    print(" 0. Exit")


def main():
    setup_logging()
    auth = AuthService()
    if not login(auth):
        return

    library = Library()
    reports = ReportService(library)

    while True:
        print_menu()
        choice = ask("Choose an option: ")
        if choice == "0":
            print("Goodbye!")
            break
        if not choice.isdigit() or not 1 <= int(choice) <= len(MENU):
            print("Please enter a number from the menu.")
            continue

        action = MENU[int(choice) - 1][1]
        try:
            action(library, reports)
        except LibraryError as error:
            print(f"Error: {error}")
        except Exception:
            logger.exception("Unexpected error")
            print("Something went wrong. Details are in library.log.")


if __name__ == "__main__":
    main()