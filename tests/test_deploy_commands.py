"""Tests for the slash-command deployment script."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from poimandres.config import BotConfig
from poimandres.deploy_commands import sync_commands


def _fake_bot() -> MagicMock:
    bot = MagicMock()
    bot.tree.sync = AsyncMock()
    bot.tree.copy_global_to = MagicMock()
    return bot


async def test_sync_commands_with_dev_guild() -> None:
    bot = _fake_bot()
    config = BotConfig(token="t", client_id=None, dev_guild_id=123)

    await sync_commands(bot, config)

    bot.tree.copy_global_to.assert_called_once()
    assert bot.tree.sync.await_count == 2


async def test_sync_commands_without_dev_guild() -> None:
    bot = _fake_bot()
    config = BotConfig(token="t", client_id=None, dev_guild_id=None)

    await sync_commands(bot, config)

    bot.tree.copy_global_to.assert_not_called()
    bot.tree.sync.assert_awaited_once()
