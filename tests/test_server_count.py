"""Tests for the standalone guild-count utility."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import discord
import pytest

from poimandres.server_count import CountClient
from poimandres.server_count import format_guild_list


def test_format_guild_list_reports_every_guild() -> None:
    alpha = MagicMock()
    alpha.name = "Alpha"
    alpha.member_count = 5

    text = format_guild_list([alpha])

    assert "Online in 1 Discord servers" in text
    assert "Alpha | Members: 5" in text
    assert "END OF PROGRAM" in text


def test_format_guild_list_handles_no_guilds() -> None:
    assert "Online in 0 Discord servers" in format_guild_list([])


async def test_count_client_on_ready_prints_and_closes(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    intents = discord.Intents.none()
    intents.guilds = True
    client = CountClient(intents=intents)
    monkeypatch.setattr(client, "close", AsyncMock())

    await client.on_ready()

    assert "Online in 0 Discord servers" in capsys.readouterr().out
    client.close.assert_awaited_once()
