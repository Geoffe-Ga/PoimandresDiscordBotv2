"""Tests for environment-based configuration loading."""

import pytest

from poimandres.config import ConfigError
from poimandres.config import load_config


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear bot variables so tests see a deterministic environment."""
    for var in ("DISCORD_TOKEN", "DISCORD_CLIENT_ID", "DISCORD_DEV_GUILD_ID"):
        monkeypatch.delenv(var, raising=False)


def test_load_config_reads_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "secret-token")

    config = load_config()

    assert config.token == "secret-token"
    assert config.client_id is None
    assert config.dev_guild_id is None


def test_load_config_parses_optional_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "t")
    monkeypatch.setenv("DISCORD_CLIENT_ID", "123")
    monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "456")

    config = load_config()

    assert config.client_id == 123
    assert config.dev_guild_id == 456


def test_load_config_missing_token_raises() -> None:
    with pytest.raises(ConfigError, match="DISCORD_TOKEN"):
        load_config()


def test_load_config_blank_token_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "   ")

    with pytest.raises(ConfigError):
        load_config()


def test_load_config_rejects_non_integer_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "t")
    monkeypatch.setenv("DISCORD_CLIENT_ID", "not-a-number")

    with pytest.raises(ConfigError, match="integer"):
        load_config()
