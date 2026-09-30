"""Input validation helpers for the Library Management System.

Each function checks one kind of user input. If the input is bad, it raises
InvalidInputError with a clear message; if it is good, it returns the
cleaned-up value.
"""

import re

from utils.exceptions import InvalidInputError

# Simple email pattern: something@something.something
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")

# IDs may contain letters, digits, hyphens and underscores (max 15 characters).
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,15}$")


def validate_non_empty(value, field_name="Value"):
    """Return the text with spaces trimmed; raise an error if it is empty."""
    text = str(value).strip()
    if not text:
        raise InvalidInputError(f"{field_name} cannot be empty.")
    return text


def validate_id(value, field_name="ID"):
    """Check an ID (book or member) and return it in upper case."""
    text = validate_non_empty(value, field_name)
    if not ID_PATTERN.match(text):
        raise InvalidInputError(
            f"{field_name} can only contain letters, digits, '-' and '_' "
            f"(maximum 15 characters)."
        )
    return text.upper()


def validate_email(value):
    """Check that the text looks like a valid email address."""
    text = validate_non_empty(value, "Email")
    if not EMAIL_PATTERN.match(text):
        raise InvalidInputError("Please enter a valid email address.")
    return text


def validate_positive_int(value, field_name="Number", maximum=None):
    """Convert the input to an integer of at least 1 (and at most maximum)."""
    try:
        number = int(str(value).strip())
    except ValueError:
        raise InvalidInputError(f"{field_name} must be a whole number.") from None
    if number < 1:
        raise InvalidInputError(f"{field_name} must be at least 1.")
    if maximum is not None and number > maximum:
        raise InvalidInputError(f"{field_name} cannot be more than {maximum}.")
    return number


def validate_choice(value, valid_choices):
    """Check that a menu choice is one of the allowed options."""
    text = str(value).strip()
    if text not in valid_choices:
        raise InvalidInputError(
            f"Invalid choice. Please pick one of: {', '.join(valid_choices)}."
        )
    return text


def validate_yes_no(value):
    """Convert a yes/no answer to True or False."""
    text = str(value).strip().lower()
    if text in ("y", "yes"):
        return True
    if text in ("n", "no"):
        return False
    raise InvalidInputError("Please answer with 'y' or 'n'.")