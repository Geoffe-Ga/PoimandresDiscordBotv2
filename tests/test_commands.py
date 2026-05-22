"""Tests for the slash-command callbacks and the contents dropdown."""

from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest
from tests.conftest import build_interaction

from poimandres.commands import ALL_COMMANDS
from poimandres.commands import ContentsSelect
from poimandres.commands import ContentsView
from poimandres.commands import register_commands

_BY_NAME = {command.name: command for command in ALL_COMMANDS}

_FLAT_KEYS = {
    "ch": "1.1",
    "ah": "1",
    "dh": "1.1",
    "al": "1.1",
    "enchiridion": "1",
    "aurelius": "1.1",
    "quran": "1.1",
    "yoga": "1.1",
    "proclus-metaphysics": "1",
}


def test_sixteen_commands_registered() -> None:
    assert len(ALL_COMMANDS) == 16


@pytest.mark.parametrize("name", sorted(_FLAT_KEYS))
async def test_flat_command_sends_embed(name: str, interaction: MagicMock) -> None:
    await _BY_NAME[name].callback(interaction, _FLAT_KEYS[name])

    interaction.response.send_message.assert_awaited_once()
    assert "embed" in interaction.response.send_message.await_args.kwargs


async def test_oh_command_sends_embed(interaction: MagicMock) -> None:
    await _BY_NAME["oh"].callback(interaction, "1")

    interaction.response.send_message.assert_awaited_once()


async def test_emeraldtablet_command_sends_embed(interaction: MagicMock) -> None:
    await _BY_NAME["emeraldtablet"].callback(interaction)

    interaction.response.send_message.assert_awaited_once()


async def test_sepher_command_verse(interaction: MagicMock) -> None:
    await _BY_NAME["sepher-yetzirah"].callback(interaction, "1.1", None)

    interaction.response.send_message.assert_awaited_once()


async def test_sepher_command_path(interaction: MagicMock) -> None:
    await _BY_NAME["sepher-yetzirah"].callback(interaction, "path", "1")

    interaction.response.send_message.assert_awaited_once()


async def test_bible_command_sends_embed(interaction: MagicMock) -> None:
    await _BY_NAME["bible"].callback(interaction, "genesis", "1.1")

    interaction.response.send_message.assert_awaited_once()


async def test_tarot_command_random(interaction: MagicMock) -> None:
    await _BY_NAME["tarot"].callback(interaction, None)

    interaction.response.send_message.assert_awaited_once()


async def test_tarot_command_specific(interaction: MagicMock) -> None:
    await _BY_NAME["tarot"].callback(interaction, "0")

    interaction.response.send_message.assert_awaited_once()


async def test_help_command_is_ephemeral(interaction: MagicMock) -> None:
    await _BY_NAME["help"].callback(interaction)

    kwargs = interaction.response.send_message.await_args.kwargs
    assert kwargs["ephemeral"] is True
    assert "embed" in kwargs


async def test_contents_command_sends_ephemeral_view(interaction: MagicMock) -> None:
    await _BY_NAME["contents"].callback(interaction)

    kwargs = interaction.response.send_message.await_args.kwargs
    assert kwargs["ephemeral"] is True
    assert isinstance(kwargs["view"], ContentsView)


def test_contents_view_has_select() -> None:
    view = ContentsView()

    assert any(isinstance(item, ContentsSelect) for item in view.children)


def test_contents_select_options_match_library() -> None:
    select = ContentsSelect()

    assert select.custom_id == "contentsSelect"
    assert len(select.options) == 13


async def test_contents_select_callback_replies_with_keys(
    interaction: MagicMock,
) -> None:
    select = ContentsSelect()
    with patch.object(
        ContentsSelect,
        "values",
        new_callable=PropertyMock,
        return_value=["ch"],
    ):
        await select.callback(interaction)

    kwargs = interaction.response.send_message.await_args.kwargs
    assert kwargs["ephemeral"] is True
    assert "/ch" in kwargs["content"]


async def test_contents_select_callback_in_dm() -> None:
    select = ContentsSelect()
    dm_interaction = build_interaction(in_guild=False)
    with patch.object(
        ContentsSelect,
        "values",
        new_callable=PropertyMock,
        return_value=["ah"],
    ):
        await select.callback(dm_interaction)

    dm_interaction.response.send_message.assert_awaited_once()


def test_register_commands_populates_tree() -> None:
    tree = MagicMock()

    register_commands(tree)

    assert tree.add_command.call_count == 16
