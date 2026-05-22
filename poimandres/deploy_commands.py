"""Standalone script that registers the slash commands with Discord.

Global commands propagate within about an hour; commands copied to the
development guild appear instantly, which is useful while iterating.
"""

from __future__ import annotations

import asyncio

import discord

from poimandres.bot import PoimandresBot
from poimandres.config import BotConfig
from poimandres.config import load_config


async def sync_commands(bot: PoimandresBot, config: BotConfig) -> None:
    """Sync application commands globally and to the dev guild if configured.

    Args:
        bot: The logged-in bot whose command tree should be synced.
        config: Configuration providing the optional development guild ID.
    """
    if config.dev_guild_id is not None:
        guild = discord.Object(id=config.dev_guild_id)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    await bot.tree.sync()


async def _main() -> None:
    """Log in, sync application commands, then disconnect."""
    config = load_config()
    bot = PoimandresBot()
    async with bot:
        await bot.login(config.token)
        await sync_commands(bot, config)
    print("Successfully reloaded application (/) commands.")


def main() -> None:
    """Console entry point for command deployment."""
    asyncio.run(_main())


if __name__ == "__main__":
    main()
