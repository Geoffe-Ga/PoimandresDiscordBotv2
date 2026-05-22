"""The Poimandres Discord client and its entry point."""

from __future__ import annotations

import logging
from datetime import datetime
from datetime import timezone

import discord
from discord import app_commands

from poimandres.banner import BANNER
from poimandres.commands import register_commands
from poimandres.config import BotConfig
from poimandres.config import load_config
from poimandres.constants import GENERIC_ERROR

_log = logging.getLogger(__name__)

_READY_RULE = "------------   ------------   ------------   ------------"
_END_RULE = "---------------------------------------------------------"


def _intents() -> discord.Intents:
    """Return the minimal intents the bot needs (guilds only)."""
    intents = discord.Intents.none()
    intents.guilds = True
    return intents


def format_invocation(interaction: discord.Interaction) -> str:
    """Build the per-invocation log line for a slash command.

    Args:
        interaction: The command interaction.

    Returns:
        A human-readable description of who invoked which command and where.
    """
    command = interaction.command
    name = command.name if command is not None else "unknown"
    if interaction.guild is None:
        return f"{name} request in DM"
    return (
        f"{name} request at {interaction.guild.name} "
        f"by {interaction.user.display_name}"
    )


def format_startup(client: discord.Client) -> str:
    """Build the startup banner, guild count and per-guild list.

    Args:
        client: The connected Discord client.

    Returns:
        The multi-line startup report printed when the bot is ready.
    """
    timestamp = datetime.now(tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    lines = [
        timestamp,
        BANNER,
        f"... ... ... Online in {len(client.guilds)} Discord servers ... ... ...",
        _READY_RULE,
    ]
    lines += [f"{guild.name} | Members: {guild.member_count}" for guild in client.guilds]
    lines += [_END_RULE, "", "...Ready!"]
    return "\n".join(lines)


async def _send_error(interaction: discord.Interaction) -> None:
    """Reply to a failed interaction with the generic ephemeral error."""
    if interaction.response.is_done():
        await interaction.followup.send(GENERIC_ERROR, ephemeral=True)
    else:
        await interaction.response.send_message(GENERIC_ERROR, ephemeral=True)


class PoimandresTree(app_commands.CommandTree[discord.Client]):
    """Command tree that reports command errors as ephemeral messages."""

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Log a command exception and report it to the invoking user."""
        _log.error("Error while executing a command", exc_info=error)
        await _send_error(interaction)


class PoimandresBot(discord.Client):
    """Discord client wiring up the Poimandres slash commands."""

    def __init__(self) -> None:
        """Create the client, build the command tree and register commands."""
        super().__init__(intents=_intents())
        self.tree = PoimandresTree(self)
        register_commands(self.tree)

    async def on_ready(self) -> None:
        """Print the startup banner and guild list."""
        print(format_startup(self))

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        """Log every slash-command invocation."""
        if interaction.type is discord.InteractionType.application_command:
            _log.info("%s", format_invocation(interaction))


def run(config: BotConfig | None = None) -> None:
    """Start the bot, blocking until it disconnects.

    Args:
        config: Pre-loaded configuration; loaded from the environment when
            omitted.
    """
    resolved = config if config is not None else load_config()
    bot = PoimandresBot()
    bot.run(resolved.token)


def main() -> None:
    """Console entry point: configure logging and run the bot."""
    logging.basicConfig(level=logging.INFO)
    run()


if __name__ == "__main__":
    main()
