"""The ASCII-art startup banner for the Poimandres bot."""

from pathlib import Path

BANNER = (Path(__file__).resolve().parent / "banner.txt").read_text(encoding="utf-8")
"""The "poimandres" ASCII banner printed on startup."""
