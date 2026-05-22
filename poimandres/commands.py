"""Slash-command definitions and the ``/contents`` dropdown view."""

from __future__ import annotations

import logging
from typing import Any
from typing import NamedTuple

import discord
from discord import app_commands

from poimandres import embeds
from poimandres.books import book_title
from poimandres.books import load_book
from poimandres.books import load_library

_log = logging.getLogger(__name__)


def _describe(name: str) -> str:
    """Return the Discord-facing description for a book-lookup command."""
    return f"Lookup {book_title(load_book(name))}"


class _FlatSpec(NamedTuple):
    """Configuration for one simple flat-lookup command."""

    name: str
    option_desc: str
    not_found: str
    normalize: bool


_FLAT_SPECS: tuple[_FlatSpec, ...] = (
    _FlatSpec("ch", "book#.verse#", "**Not found**\ntry: `/ch  1.2`", normalize=True),
    _FlatSpec("ah", "# 1-41", "**Not found**\ntry: `/ah  1`", normalize=True),
    _FlatSpec("dh", "1.1 - 10.7", "**Not found**\ntry: `/dh  1.1`", normalize=True),
    _FlatSpec("al", "chapter#.verse#", "**Not found**\ntry: `/al  3.75`", normalize=True),
    _FlatSpec(
        "enchiridion",
        "# 1-51",
        "**Not found**\ntry: `/enchiridion  27`",
        normalize=True,
    ),
    _FlatSpec(
        "aurelius",
        "book#.line#",
        "**Not found**\ntry: `/aurelius  1.16`",
        normalize=True,
    ),
    _FlatSpec("quran", "Surah#.Ayah#", "**Not found** Try: `/quran 1.1`", normalize=True),
    _FlatSpec("yoga", "Pāda#.sūtra#", "**Not found**\ntry: `/yoga  1.1`", normalize=True),
    _FlatSpec(
        "proclus-metaphysics",
        "# 1-211",
        "**Not found**\ntry: `/proclus-metaphysics  1`",
        normalize=False,
    ),
)


def _make_flat_command(spec: _FlatSpec) -> app_commands.Command[Any, ..., None]:
    """Build a slash command for one simple flat-lookup text.

    Args:
        spec: The per-command configuration.

    Returns:
        A registered application command.
    """

    @app_commands.command(name=spec.name, description=_describe(spec.name))
    @app_commands.describe(part=spec.option_desc)
    async def _command(interaction: discord.Interaction, part: str) -> None:
        """Reply with the requested passage embed."""
        embed = embeds.flat_lookup_embed(
            load_book(spec.name),
            part,
            spec.not_found,
            normalize=spec.normalize,
        )
        await interaction.response.send_message(embed=embed)

    return _command


_FLAT_COMMANDS: tuple[app_commands.Command[Any, ..., None], ...] = tuple(
    _make_flat_command(spec) for spec in _FLAT_SPECS
)


@app_commands.command(name="oh", description=_describe("oh"))
@app_commands.describe(fragment="# 1-5")
async def _oh(interaction: discord.Interaction, fragment: str) -> None:
    """Look up an Oxford Fragments passage."""
    embed = embeds.oxford_embed(load_book("oh"), fragment, "**Not found**\ntry: `/oh 1`")
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="emeraldtablet", description=_describe("emeraldtablet"))
async def _emeraldtablet(interaction: discord.Interaction) -> None:
    """Show the full Emerald Tablet text."""
    embed = embeds.emerald_embed(load_book("emeraldtablet"))
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="sepher-yetzirah", description=_describe("sepher-yetzirah"))
@app_commands.describe(part="chapter#.line#", path="(optional) 1-32")
async def _sepher_yetzirah(
    interaction: discord.Interaction,
    part: str,
    path: str | None = None,
) -> None:
    """Look up a Sepher Yetzirah passage or path."""
    embed = embeds.sepher_embed(load_book("sepher-yetzirah"), part, path)
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="bible", description=_describe("bible"))
@app_commands.describe(book="ie. genesis", chapterverse="ie. 1.1")
async def _bible(
    interaction: discord.Interaction,
    book: str,
    chapterverse: str,
) -> None:
    """Look up a Bible verse."""
    embed = embeds.bible_embed(load_book("bible"), book, chapterverse)
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="tarot", description="Pull a RWS Tarot Card")
@app_commands.describe(card="(optional) number of card (0-77)")
async def _tarot(interaction: discord.Interaction, card: str | None = None) -> None:
    """Pull a tarot card image."""
    await interaction.response.send_message(embed=embeds.tarot_embed(card))


@app_commands.command(name="help", description="List the texts Poimandres can access")
async def _help(interaction: discord.Interaction) -> None:
    """List every text the bot can quote."""
    await interaction.response.send_message(embed=embeds.help_embed(), ephemeral=True)


@app_commands.command(
    name="contents",
    description='Get a "contents page" of the available texts',
)
async def _contents(interaction: discord.Interaction) -> None:
    """Show the dropdown text picker."""
    await interaction.response.send_message(view=ContentsView(), ephemeral=True)


def _selection_actor(interaction: discord.Interaction) -> str:
    """Describe who made a dropdown selection, for logging."""
    if interaction.guild is None:
        return "in DM"
    return f"by {interaction.user.display_name}"


class ContentsSelect(discord.ui.Select[discord.ui.View]):
    """Dropdown listing every text; replies with that text's lookup keys."""

    def __init__(self) -> None:
        """Populate the dropdown options from ``LIBRARY.json``."""
        options = [
            discord.SelectOption(label=entry["label"], value=entry["value"])
            for entry in load_library()
        ]
        super().__init__(
            custom_id="contentsSelect",
            placeholder="Select a text...",
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """Reply with the valid lookup keys for the chosen text."""
        value = self.values[0]
        _log.info("%s selected %s", value, _selection_actor(interaction))
        text = embeds.contents_text(value, load_book(value))
        await interaction.response.send_message(content=text, ephemeral=True)


class ContentsView(discord.ui.View):
    """Container view holding the contents dropdown."""

    def __init__(self) -> None:
        """Attach a fresh contents dropdown to the view."""
        super().__init__()
        self.add_item(ContentsSelect())


ALL_COMMANDS: tuple[app_commands.Command[Any, ..., None], ...] = (
    *_FLAT_COMMANDS,
    _oh,
    _emeraldtablet,
    _sepher_yetzirah,
    _bible,
    _tarot,
    _help,
    _contents,
)
"""Every slash command exposed by the bot."""


def register_commands(tree: app_commands.CommandTree[Any]) -> None:
    """Add every Poimandres slash command to the given command tree.

    Args:
        tree: The command tree to populate.
    """
    for command in ALL_COMMANDS:
        tree.add_command(command)
