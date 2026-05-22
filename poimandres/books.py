"""Loading and accessing the verbatim JSON text corpora."""

from __future__ import annotations

from functools import cache
import json
from pathlib import Path
from typing import Any

BOOKS_DIR = Path(__file__).resolve().parent.parent / "books"
"""Directory holding the verbatim corpus JSON files."""

METADATA_KEYS = frozenset({"bookTitle", "translator"})
"""Keys present in book JSON files that hold metadata, not passage text."""


@cache
def load_book(name: str) -> dict[str, Any]:
    """Load and cache a book's JSON data.

    Args:
        name: The book's file stem (e.g. ``"ch"``), without the extension.

    Returns:
        The parsed JSON object mapping keys to passage text or metadata.
    """
    path = BOOKS_DIR / f"{name}.json"
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


@cache
def load_library() -> list[dict[str, str]]:
    """Load the dropdown index used by ``/contents``.

    Returns:
        A list of ``{"label", "value"}`` option dictionaries.
    """
    path = BOOKS_DIR / "LIBRARY.json"
    data: list[dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
    return data


def book_title(book: dict[str, Any]) -> str:
    """Return a book's ``bookTitle`` metadata field as a string."""
    return str(book["bookTitle"])


def book_translator(book: dict[str, Any]) -> str:
    """Return a book's ``translator`` metadata field as a string."""
    return str(book["translator"])


def text_keys(book: dict[str, Any]) -> list[str]:
    """Return every key whose value is passage text, excluding metadata.

    Keys whose value is a nested object (such as Sepher Yetzirah's ``path``)
    are also dropped, so the result is always safe to draw a random passage
    from.

    Args:
        book: The loaded book JSON.

    Returns:
        Every passage key of the book.
    """
    return [
        key
        for key, value in book.items()
        if key not in METADATA_KEYS and isinstance(value, str)
    ]
