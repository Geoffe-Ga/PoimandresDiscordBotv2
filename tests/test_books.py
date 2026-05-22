"""Tests for corpus loading helpers."""

from poimandres.books import book_title
from poimandres.books import book_translator
from poimandres.books import load_book
from poimandres.books import load_library
from poimandres.books import text_keys


def test_load_book_returns_passages_and_metadata() -> None:
    book = load_book("ch")

    assert book["bookTitle"] == "The Corpus Hermeticum"
    assert isinstance(book["1.1"], str)


def test_load_book_is_cached() -> None:
    assert load_book("ah") is load_book("ah")


def test_load_library_has_expected_entries() -> None:
    library = load_library()

    values = {entry["value"] for entry in library}
    assert {"ch", "bible", "tarot"} <= values
    assert all({"label", "value"} == set(entry) for entry in library)


def test_book_title_and_translator() -> None:
    book = load_book("ch")

    assert book_title(book) == "The Corpus Hermeticum"
    assert book_translator(book) == "G.R.S. Mead"


def test_text_keys_excludes_metadata() -> None:
    keys = text_keys(load_book("ch"))

    assert "bookTitle" not in keys
    assert "translator" not in keys
    assert "1.1" in keys


def test_text_keys_excludes_nested_objects() -> None:
    keys = text_keys(load_book("sepher-yetzirah"))

    assert "path" not in keys
    assert "1.1" in keys
