"""Pure builders that turn user input plus corpus data into Discord embeds.

Every function here is side-effect free and independent of the Discord
gateway, which keeps the lookup behaviour fully unit-testable.
"""

from __future__ import annotations

import secrets
from typing import Any

import discord

from poimandres.books import METADATA_KEYS
from poimandres.books import book_title
from poimandres.books import book_translator
from poimandres.books import passage_keys
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
    "**Not found**\n"
    "try: `/sepher-yetzirah  1.1`\n"
    "or: `/sepher-yetzirah path 1`"
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


def normalize_key(raw: str) -> str:
    """Replace ``:`` with ``.`` so ``1:2`` and ``1.2`` are equivalent."""
    return raw.replace(":", ".")


def lookup_passage(book: dict[str, Any], key: str) -> str | None:
    """Return the passage text stored at ``key``.

    Args:
        book: The loaded book JSON.
        key: The lookup key to resolve.

    Returns:
        The passage text, or ``None`` if the key is missing or names a
        metadata field rather than a passage.
    """
    if key in METADATA_KEYS:
        return None
    value = book.get(key)
    return value if isinstance(value, str) else None


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
    key: str,
    not_found: str,
    *,
    normalize: bool = True,
) -> discord.Embed:
    """Build the embed for a simple flat-lookup command.

    Args:
        book: The loaded book JSON.
        key: The user-supplied lookup key.
        not_found: Body shown when the key is missing.
        normalize: Whether to apply ``:`` -> ``.`` normalisation.

    Returns:
        A configured Discord embed.
    """
    if normalize:
        key = normalize_key(key)
    passage = lookup_passage(book, key)
    body = passage if passage is not None else not_found
    footer = f"{book_title(book)} | {key} | {book_translator(book)}"
    return _passage_embed(body, footer)


def oxford_embed(
    book: dict[str, Any],
    fragment: str,
    not_found: str,
) -> discord.Embed:
    """Build the ``/oh`` embed, which adds a title and external URL.

    Args:
        book: The loaded ``oh`` JSON.
        fragment: The user-supplied fragment number.
        not_found: Body shown when the fragment is missing.

    Returns:
        A configured Discord embed.
    """
    passage = lookup_passage(book, fragment)
    body = passage if passage is not None else not_found
    title = f"{book_title(book)} | Translated by {book_translator(book)}"
    footer = f"{book_title(book)} | {fragment} | {book_translator(book)}"
    return _passage_embed(body, footer, title=title, url=OXFORD_URL)


def emerald_embed(book: dict[str, Any]) -> discord.Embed:
    """Build the ``/emeraldtablet`` embed from the book's ``message`` field."""
    body = str(book["message"])
    footer = f"{book_title(book)} | {EMERALD_FOOTER_SUFFIX}"
    return _passage_embed(body, footer)


def _sepher_body(book: dict[str, Any], part: str, path: str | None) -> str:
    """Resolve the body text for a ``/sepher-yetzirah`` lookup."""
    if part == "path":
        nested = book.get("path")
        if isinstance(nested, dict) and path is not None:
            value = nested.get(path)
            if isinstance(value, str):
                return value
        return SEPHER_NOT_FOUND
    passage = lookup_passage(book, part)
    return passage if passage is not None else SEPHER_NOT_FOUND


def sepher_embed(
    book: dict[str, Any],
    part: str,
    path: str | None,
) -> discord.Embed:
    """Build the ``/sepher-yetzirah`` embed.

    Args:
        book: The loaded ``sepher-yetzirah`` JSON.
        part: The chapter/line key, or the literal ``"path"``.
        path: The optional path number (``1``-``32``).

    Returns:
        A configured Discord embed.
    """
    part = normalize_key(part)
    body = _sepher_body(book, part, path)
    path_str = path if path is not None else ""
    footer = f"{book_title(book)} | {part} {path_str} | {book_translator(book)}"
    return _passage_embed(body, footer)


def _bible_body(
    book: dict[str, Any],
    book_name: str,
    chapterverse: str,
) -> tuple[str, str]:
    """Resolve the body text and final chapter/verse for a Bible lookup."""
    chapter = book.get(book_name)
    if not isinstance(chapter, dict):
        return BIBLE_NOT_FOUND, chapterverse
    if chapterverse == "X":
        chapterverse = secrets.choice(list(chapter.keys()))
    value = chapter.get(chapterverse)
    body = value if isinstance(value, str) else BIBLE_NOT_FOUND
    return body, chapterverse


def bible_embed(
    book: dict[str, Any],
    book_name: str,
    chapterverse: str,
) -> discord.Embed:
    """Build the ``/bible`` embed, supporting ``X`` for random selection.

    Args:
        book: The loaded ``bible`` JSON.
        book_name: The book name, or ``X`` for a random book.
        chapterverse: The ``chapter.verse`` key, or ``X`` for a random verse.

    Returns:
        A configured Discord embed.
    """
    book_name = book_name.upper()
    chapterverse = normalize_key(chapterverse)
    if book_name == "X":
        book_name = secrets.choice(passage_keys(book))
    body, chapterverse = _bible_body(book, book_name, chapterverse)
    footer = f"{book_title(book)} | {book_name}  {chapterverse}"
    return _passage_embed(body, footer)


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
    body = f"`/{value}` + *one of the following:*\n`{chips}`"
    if len(body) > _CONTENTS_LIMIT:
        body = body[:_CONTENTS_TRUNCATE] + _CONTENTS_OVERFLOW
    return body
