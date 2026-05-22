"""Tests for the Discord client wiring and entry point."""

import logging
from unittest.mock import MagicMock

import discord
from discord import app_commands
import pytest

from poimandres import bot
from poimandres.bot import PoimandresBot
from poimandres.bot import format_invocation
from poimandres.bot import format_startup
from poimandres.bot import main
from poimandres.bot import run
from poimandres.config import BotConfig


def _guild(name: str, members: int) -> MagicMock:
    guild = MagicMock()
    guild.name = name
    guild.member_count = members
    return guild


def test_bot_uses_guild_only_intents() -> None:
    client = PoimandresBot()

    assert client.intents.guilds is True
    assert client.intents.members is False


def test_bot_registers_all_commands() -> None:
    client = PoimandresBot()

    assert len(client.tree.get_commands()) == 16


def test_format_invocation_in_guild() -> None:
    interaction = MagicMock()
    interaction.command.name = "ch"
    interaction.guild = _guild("Hermetica", 1)
    interaction.user.display_name = "Seeker"

    assert format_invocation(interaction) == "ch request at Hermetica by Seeker"


def test_format_invocation_in_dm() -> None:
    interaction = MagicMock()
    interaction.command.name = "ch"
    interaction.guild = None

    assert format_invocation(interaction) == "ch request in DM"


def test_format_invocation_unknown_command() -> None:
    interaction = MagicMock()
    interaction.command = None
    interaction.guild = None

    assert format_invocation(interaction) == "unknown request in DM"


def test_format_startup_lists_every_guild() -> None:
    client = MagicMock()
    client.guilds = [_guild("Alpha", 3), _guild("Beta", 7)]

    text = format_startup(client)

    assert "Online in 2 Discord servers" in text
    assert "Alpha | Members: 3" in text
    assert "Beta | Members: 7" in text
    assert text.endswith("...Ready!")


async def test_on_ready_prints_startup(capsys: pytest.CaptureFixture[str]) -> None:
    client = PoimandresBot()

    await client.on_ready()

    assert "Online in 0 Discord servers" in capsys.readouterr().out


async def test_on_interaction_logs_command(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = PoimandresBot()
    interaction = MagicMock()
    interaction.type = discord.InteractionType.application_command
    interaction.command.name = "ch"
    interaction.guild = None

    with caplog.at_level(logging.INFO):
        await client.on_interaction(interaction)

    assert "ch request in DM" in caplog.text


async def test_on_interaction_ignores_non_command(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = PoimandresBot()
    interaction = MagicMock()
    interaction.type = discord.InteractionType.component

    with caplog.at_level(logging.INFO):
        await client.on_interaction(interaction)

    assert not any(record.name == "poimandres.bot" for record in caplog.records)


async def test_tree_on_error_replies_to_user(interaction: MagicMock) -> None:
    tree = PoimandresBot().tree

    await tree.on_error(interaction, app_commands.AppCommandError("boom"))

    interaction.response.send_message.assert_awaited_once()


async def test_tree_on_error_uses_followup_when_done(
    done_interaction: MagicMock,
) -> None:
    tree = PoimandresBot().tree

    await tree.on_error(done_interaction, app_commands.AppCommandError("boom"))

    done_interaction.followup.send.assert_awaited_once()


def test_run_uses_provided_config(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}
    monkeypatch.setattr(
        PoimandresBot,
        "run",
        lambda _self, token: captured.update(token=token),
    )

    run(BotConfig(token="abc", client_id=None, dev_guild_id=None))

    assert captured["token"] == "abc"


def test_run_loads_config_when_omitted(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}
    monkeypatch.setattr(
        PoimandresBot,
        "run",
        lambda _self, token: captured.update(token=token),
    )
    monkeypatch.setattr(
        bot,
        "load_config",
        lambda: BotConfig(token="from-env", client_id=None, dev_guild_id=None),
    )

    run()

    assert captured["token"] == "from-env"


def test_main_configures_logging_and_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(bot, "run", lambda: calls.append("run"))
    monkeypatch.setattr(bot.logging, "basicConfig", lambda **_k: calls.append("log"))

    main()

    assert calls == ["log", "run"]
