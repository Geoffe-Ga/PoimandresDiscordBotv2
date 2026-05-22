"""Pure builders that turn user input plus corpus data into Discord embeds.

Every function here is side-effect free and independent of the Discord
gateway, which keeps the lookup behaviour fully unit-testable.
"""

from __future__ import annotations

import re
import secrets
from typing import Any

import discord

from poimandres.books import METADATA_KEYS
from poimandres.books import book_title
from poimandres.books import book_translator
from poimandres.books import text_keys
from poimandres.constants import EMBED_COLOR
from poimandres.help_content import HELP_DESCRIPTION
from poimandres.help_content import HELP_FIELDS
from poimandres.help_content import HELP_FOOTER
from poimandres.tarot_cards import TAROT_CARDS

OXFORD_URL = "https://sartrix.wordpress.com/the-oxford-hermetica/"
"""External link attached to the ``/oh`` embed."""

EMERALD_FOOTER_SUFFIX = "12th Century Latin Version"
"""Hardcoded translator stand-in for the ``/emeraldtablet`` footer."""

SEPHER_NOT_FOUND = (
    "**Not found**\ntry: `/sepher-yetzirah  1.1`\nor: `/sepher-yetzirah path 1`"
)
"""Not-found body for ``/sepher-yetzirah``."""

BIBLE_NOT_FOUND = "**Not found**\ntry: `/bible genesis 1.1`"
"""Not-found body for ``/bible``."""

TAROT_NOT_FOUND = "**Not found**\ntry: `/tarot 0-77`"
"""Body shown when ``/tarot`` is given an out-of-range card number."""

_CONTENTS_LIMIT = 950
"""Maximum length of a ``/contents`` reply before it is truncated."""

_CONTENTS_TRUNCATE = 901
"""Number of characters kept when a ``/contents`` reply is truncated."""

_CONTENTS_OVERFLOW = " ***... Discord message limit exceeded.***"
"""Suffix appended to a truncated ``/contents`` reply."""

_SEPARATOR_RE = re.compile(r"[\s.:;,\-]+")
"""Matches any run of the separators treated as equivalent in lookup keys."""


def canonical_key(raw: str) -> str:
    """Reduce a lookup key to a separator- and zero-insensitive form.

    Whitespace and the ``. : ; , -`` separators are all treated alike, and
    purely numeric segments lose any leading zeros, so ``1:2``, ``01.02``,
    ``1 2`` and ``1-2`` all canonicalise to ``1.2``.

    Args:
        raw: The user-supplied (or stored) key.

    Returns:
        The canonical comparison form of ``raw``.
    """
    segments = (seg for seg in _SEPARATOR_RE.split(raw.strip()) if seg)
    return ".".join(str(int(seg)) if seg.isdigit() else seg.lower() for seg in segments)


def resolve_key(book: dict[str, Any], raw: str) -> str | None:
    """Find the stored passage key matching loosely-typed user input.

    Args:
        book: The loaded book JSON, or a nested chapter object.
        raw: The user-supplied key, in any separator or zero-padding style.

    Returns:
        The matching key exactly as stored in ``book``, or ``None`` when no
        passage key shares its canonical form.
    """
    target = canonical_key(raw)
    if not target:
        return None
    for key, value in book.items():
        if key in METADATA_KEYS or not isinstance(value, str):
            continue
        if canonical_key(key) == target:
            return key
    return None


def _resolve_or_random(book: dict[str, Any], key: str | None) -> str | None:
    """Resolve ``key``, or draw a random passage key when it is ``None``."""
    if key is None:
        return secrets.choice(text_keys(book))
    return resolve_key(book, key)


def _passage_embed(
    body: str,
    footer: str,
    *,
    title: str | None = None,
    url: str | None = None,
) -> discord.Embed:
    """Build a standard passage embed with the shared accent colour."""
    embed = discord.Embed(
        color=EMBED_COLOR,
        description=body,
        title=title,
        url=url,
    )
    embed.set_footer(text=footer)
    return embed


def flat_lookup_embed(
    book: dict[str, Any],
    key: str | None,
    not_found: str,
) -> discord.Embed:
    """Build the embed for a simple flat-lookup command.

    Args:
        book: The loaded book JSON.
        key: The user-supplied lookup key, or ``None`` to draw a random
            passage (bibliomancy).
        not_found: Body shown when the key cannot be resolved.

    Returns:
        A configured Discord embed.
    """
    resolved = _resolve_or_random(book, key)
    if resolved is None:
        footer = f"{book_title(book)} | {book_translator(book)}"
        return _passage_embed(not_found, footer)
    footer = f"{book_title(book)} | {resolved} | {book_translator(book)}"
    return _passage_embed(str(book[resolved]), footer)


def oxford_embed(
    book: dict[str, Any],
    fragment: str | None,
    not_found: str,
) -> discord.Embed:
    """Build the ``/oh`` embed, which adds a title and external URL.

    Args:
        book: The loaded ``oh`` JSON.
        fragment: The fragment number, or ``None`` to draw a random fragment.
        not_found: Body shown when the fragment cannot be resolved.

    Returns:
        A configured Discord embed.
    """
    title = f"{book_title(book)} | Translated by {book_translator(book)}"
    resolved = _resolve_or_random(book, fragment)
    if resolved is None:
        footer = f"{book_title(book)} | {book_translator(book)}"
        return _passage_embed(not_found, footer, title=title, url=OXFORD_URL)
    footer = f"{book_title(book)} | {resolved} | {book_translator(book)}"
    return _passage_embed(str(book[resolved]), footer, title=title, url=OXFORD_URL)


def emerald_embed(book: dict[str, Any]) -> discord.Embed:
    """Build the ``/emeraldtablet`` embed from the book's ``message`` field."""
    body = str(book["message"])
    footer = f"{book_title(book)} | {EMERALD_FOOTER_SUFFIX}"
    return _passage_embed(body, footer)


def _sepher_path_embed(book: dict[str, Any], path: str | None) -> discord.Embed:
    """Build a Sepher Yetzirah ``path`` embed, random when ``path`` is ``None``."""
    title = book_title(book)
    translator = book_translator(book)
    nested = book.get("path")
    if not isinstance(nested, dict):
        return _passage_embed(SEPHER_NOT_FOUND, f"{title} | path | {translator}")
    resolved = _resolve_or_random(nested, path)
    if resolved is None:
        return _passage_embed(SEPHER_NOT_FOUND, f"{title} | path | {translator}")
    footer = f"{title} | path {resolved} | {translator}"
    return _passage_embed(str(nested[resolved]), footer)


def sepher_embed(
    book: dict[str, Any],
    part: str | None,
    path: str | None,
) -> discord.Embed:
    """Build the ``/sepher-yetzirah`` embed.

    Args:
        book: The loaded ``sepher-yetzirah`` JSON.
        part: A chapter/line key, the literal ``"path"``, or ``None`` to draw
            a random passage. If ``part`` is omitted but ``path`` is supplied,
            the lookup is treated as a path lookup as a convenience.
        path: A path number (``1``-``32``), or ``None``.

    Returns:
        A configured Discord embed.
    """
    is_path = part is not None and part.strip().lower() == "path"
    if is_path or (part is None and path is not None):
        return _sepher_path_embed(book, path)
    title = book_title(book)
    translator = book_translator(book)
    resolved = _resolve_or_random(book, part)
    if resolved is None:
        return _passage_embed(SEPHER_NOT_FOUND, f"{title} |  | {translator}")
    footer = f"{title} | {resolved}  | {translator}"
    return _passage_embed(str(book[resolved]), footer)


def _bible_book_key(name: str) -> str:
    """Reduce a Bible book name to an alphanumeric-only uppercase form."""
    return "".join(char for char in name.upper() if char.isalnum())


def _random_bible_book(book: dict[str, Any]) -> str:
    """Pick a random Bible book key."""
    candidates = [
        key
        for key, value in book.items()
        if key not in METADATA_KEYS and isinstance(value, dict)
    ]
    return secrets.choice(candidates)


def _resolve_bible_book(book: dict[str, Any], name: str) -> str | None:
    """Find the stored Bible book key matching a loosely-typed name."""
    if name.strip().upper() == "X":
        return _random_bible_book(book)
    target = _bible_book_key(name)
    if not target:
        return None
    for key, value in book.items():
        if key in METADATA_KEYS or not isinstance(value, dict):
            continue
        if _bible_book_key(key) == target:
            return key
    return None


def _resolve_bible_verse(chapter: dict[str, Any], verse: str | None) -> str | None:
    """Resolve a Bible verse key, random when ``verse`` is ``None`` or ``X``."""
    if verse is None or verse.strip().upper() == "X":
        return secrets.choice(text_keys(chapter))
    return resolve_key(chapter, verse)


def bible_embed(
    book: dict[str, Any],
    book_name: str | None,
    chapterverse: str | None,
) -> discord.Embed:
    """Build the ``/bible`` embed.

    Either argument may be omitted (or passed as ``X``) to draw a random book
    and/or verse.

    Args:
        book: The loaded ``bible`` JSON.
        book_name: A book name, or ``None``/``X`` for a random book.
        chapterverse: A ``chapter.verse`` key, or ``None``/``X`` for a random
            verse.

    Returns:
        A configured Discord embed.
    """
    title = book_title(book)
    if book_name is None:
        resolved_book: str | None = _random_bible_book(book)
    else:
        resolved_book = _resolve_bible_book(book, book_name)
    if resolved_book is None:
        return _passage_embed(BIBLE_NOT_FOUND, f"{title} | not found")
    chapter = book[resolved_book]
    resolved_verse = _resolve_bible_verse(chapter, chapterverse)
    if resolved_verse is None:
        return _passage_embed(BIBLE_NOT_FOUND, f"{title} | {resolved_book}")
    footer = f"{title} | {resolved_book}  {resolved_verse}"
    return _passage_embed(str(chapter[resolved_verse]), footer)


def _parse_card_index(card: str) -> int | None:
    """Parse a tarot card number, or ``None`` if it is invalid or out of range."""
    try:
        index = int(card)
    except ValueError:
        return None
    if 0 <= index < len(TAROT_CARDS):
        return index
    return None


def _tarot_image_embed(url: str) -> discord.Embed:
    """Build a tarot embed showing a single card image."""
    embed = discord.Embed(color=EMBED_COLOR)
    embed.set_image(url=url)
    return embed


def tarot_embed(card: str | None) -> discord.Embed:
    """Build the ``/tarot`` embed.

    Args:
        card: The requested 0-indexed card number, or ``None`` for a random
            pull.

    Returns:
        An embed showing the card image, or a not-found embed when ``card``
        is out of the ``0``-``77`` range.
    """
    if card is None:
        return _tarot_image_embed(secrets.choice(TAROT_CARDS))
    index = _parse_card_index(card)
    if index is None:
        return discord.Embed(color=EMBED_COLOR, description=TAROT_NOT_FOUND)
    return _tarot_image_embed(TAROT_CARDS[index])


def help_embed() -> discord.Embed:
    """Build the static ``/help`` embed listing every available text."""
    embed = discord.Embed(
        color=EMBED_COLOR,
        description=HELP_DESCRIPTION,
        timestamp=discord.utils.utcnow(),
    )
    for name, value, inline in HELP_FIELDS:
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_footer(text=HELP_FOOTER)
    return embed


def contents_text(value: str, book: dict[str, Any]) -> str:
    """Build the ``/contents`` reply listing every lookup key of a text.

    Args:
        value: The chosen book's command/JSON name.
        book: The loaded JSON for that book.

    Returns:
        A message body with the keys rendered as inline-code chips,
        truncated if it would exceed Discord's message limit.
    """
    chips = ",".join(book.keys())
    chips = chips.replace(",", "` `").replace("bookTitle", "").replace("translator", "")
    body = (
        f"`/{value}` + *one of the following* "
        f"(or nothing, for a random passage):\n`{chips}`"
    )
    if len(body) > _CONTENTS_LIMIT:
        body = body[:_CONTENTS_TRUNCATE] + _CONTENTS_OVERFLOW
    return body
