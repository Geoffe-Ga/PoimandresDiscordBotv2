"""Shared test fixtures and helpers."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import discord
import pytest


def build_interaction(*, in_guild: bool = True, response_done: bool = False) -> MagicMock:
    """Build a fake ``discord.Interaction`` for exercising command callbacks.

    Args:
        in_guild: Whether the interaction originates from a guild (vs. a DM).
        response_done: Whether the interaction response has already been sent.

    Returns:
        A configured mock interaction.
    """
    interaction = MagicMock(spec=discord.Interaction)

    response = MagicMock()
    response.send_message = AsyncMock()
    response.is_done = MagicMock(return_value=response_done)
    interaction.response = response

    followup = MagicMock()
    followup.send = AsyncMock()
    interaction.followup = followup

    if in_guild:
        guild = MagicMock()
        guild.name = "Test Guild"
        interaction.guild = guild
    else:
        interaction.guild = None

    user = MagicMock()
    user.display_name = "Tester"
    interaction.user = user

    return interaction


@pytest.fixture
def interaction() -> MagicMock:
    """Return a fake guild interaction with an unsent response."""
    return build_interaction()


@pytest.fixture
def done_interaction() -> MagicMock:
    """Return a fake interaction whose response has already been sent."""
    return build_interaction(response_done=True)
