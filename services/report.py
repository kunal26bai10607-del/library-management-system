"""Reports for the Library Management System.

Each report returns a list of text lines, so it is easy to print and
easy to test.
"""

from datetime import date

FINE_PER_DAY = 2  # Rs. per late day, matching the fine rule in member.py


def format_table(headers, rows):
    """Turn headers and rows into neatly aligned text lines."""
    rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def build(cells):
        return " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells))

    lines = [build(headers), "-+-".join("-" * w for w in widths)]
    lines.extend(build(row) for row in rows)
    return lines


class ReportService:
    """Builds text reports from the Library data."""

    def __init__(self, library):
        self.library = library

    def books_report(self):
        rows = [
            (b.book_id, b.title, b.author, b.available_copies, b.total_copies)
            for b in self.library.list_books()
        ]
        if not rows:
            return ["No books in the library yet."]
        return format_table(
            ["ID", "Title", "Author", "Available", "Total"], rows
        )

    def members_report(self):
        rows = [
            (m.member_id, m.name, m.email, m.member_type, len(m.borrowed_books))
            for m in self.library.list_members()
        ]
        if not rows:
            return ["No members registered yet."]
        return format_table(
            ["ID", "Name", "Email", "Type", "Books held"], rows
        )

    def overdue_report(self, on_date=None):
        on_date = on_date or date.today()
        rows = []
        for t in self.library.overdue_transactions(on_date):
            days = (on_date - t.due_date).days
            rows.append(
                (t.member_id, t.book_id, t.due_date, days, days * FINE_PER_DAY)
            )
        if not rows:
            return ["No overdue books."]
        return format_table(
            ["Member", "Book", "Due date", "Days late", "Fine so far (Rs.)"],
            rows,
        )

    def member_history_report(self, member_id):
        history = self.library.member_history(member_id)
        if not history:
            return ["This member has no transactions yet."]
        rows = [
            (t.transaction_id, t.book_id, t.issue_date, t.due_date,
             t.return_date or "Not returned", t.fine)
            for t in history
        ]
        return format_table(
            ["Txn", "Book", "Issued", "Due", "Returned", "Fine (Rs.)"], rows
        )

    def summary_report(self):
        books = self.library.list_books()
        return [
            f"Book titles       : {len(books)}",
            f"Total copies      : {sum(b.total_copies for b in books)}",
            f"Copies issued now : {len(self.library.active_transactions())}",
            f"Members           : {len(self.library.list_members())}",
            f"Overdue books     : {len(self.library.overdue_transactions())}",
        ]