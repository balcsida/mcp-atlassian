"""Tests for project dependency declarations."""

from pathlib import Path


def test_fastmcp_minimum_version_includes_event_store() -> None:
    """Ensure allowed FastMCP versions include fastmcp.server.event_store."""
    pyproject = Path("pyproject.toml").read_text()

    assert '"fastmcp>=3.2.0,<4.0.0"' in pyproject
