"""Loading and accessing the verbatim JSON text corpora."""

from __future__ import annotations

import json
from functools import cache
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


def passage_keys(book: dict[str, Any]) -> list[str]:
    """Return every lookup key of a book, excluding metadata keys."""
    return [key for key in book if key not in METADATA_KEYS]
