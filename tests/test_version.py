"""Smoke test: the package imports cleanly and exposes its version."""

from poimandres import __version__


def test_version_is_defined() -> None:
    assert __version__ == "2.0.0"
