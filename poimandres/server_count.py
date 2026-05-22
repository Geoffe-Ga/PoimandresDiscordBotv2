"""Standalone utility that prints the bot's guild list, then exits."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable

import discord

from poimandres.banner import BANNER
from poimandres.config import load_config

_RULE = "==========================================================="


def format_guild_list(guilds: Iterable[discord.Guild]) -> str:
    """Build the banner and per-guild member-count report.

    Args:
        guilds: The guilds the bot belongs to.

    Returns:
        The multi-line report printed before the utility exits.
    """
    guild_list = list(guilds)
    lines = [
        BANNER,
        f"... ... ... Online in {len(guild_list)} Discord servers ... ... ...",
        _RULE,
    ]
    lines += [f"{guild.name} | Members: {guild.member_count}" for guild in guild_list]
    lines += [_RULE, "", "\t\t~ END OF PROGRAM ~"]
    return "\n".join(lines)


class CountClient(discord.Client):
    """Minimal client that prints its guild list once ready, then closes."""

    async def on_ready(self) -> None:
        """Print the guild list and disconnect."""
        print(format_guild_list(self.guilds))
        await self.close()


async def _main() -> None:
    """Connect, print the guild list, and disconnect."""
    config = load_config()
    intents = discord.Intents.none()
    intents.guilds = True
    client = CountClient(intents=intents)
    async with client:
        await client.start(config.token)


def main() -> None:
    """Console entry point for the guild-count utility."""
    asyncio.run(_main())


if __name__ == "__main__":
    main()
