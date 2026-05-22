"""Environment-based configuration for the Poimandres bot.

Configuration is read directly from the process environment. In production the
bot runs on Railway, which injects service variables into the environment; for
local development use ``railway run`` to do the same.
"""

from __future__ import annotations

import os
from typing import NamedTuple


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or malformed."""


class BotConfig(NamedTuple):
    """Runtime configuration loaded from the environment."""

    token: str
    client_id: int | None
    dev_guild_id: int | None


def _optional_int(name: str) -> int | None:
    """Read an environment variable as an integer.

    Args:
        name: The environment variable to read.

    Returns:
        The parsed integer, or ``None`` when the variable is unset or empty.

    Raises:
        ConfigError: If the variable is set but is not a valid integer.
    """
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        message = f"{name} must be an integer, got {raw!r}."
        raise ConfigError(message) from exc


def load_config() -> BotConfig:
    """Load bot configuration from environment variables.

    Returns:
        The populated configuration.

    Raises:
        ConfigError: If ``DISCORD_TOKEN`` is not set.
    """
    token = os.environ.get("DISCORD_TOKEN", "").strip()
    if not token:
        message = (
            "DISCORD_TOKEN is not set; add it to the Railway service variables "
            "(or run locally with `railway run`)."
        )
        raise ConfigError(message)
    return BotConfig(
        token=token,
        client_id=_optional_int("DISCORD_CLIENT_ID"),
        dev_guild_id=_optional_int("DISCORD_DEV_GUILD_ID"),
    )
