"""Unit tests for Atlassian opaque token verifier."""

from __future__ import annotations

import time

import pytest
from fastmcp.server.auth.auth import AccessToken

from mcp_atlassian.utils.token_verifier import (
    TOKEN_CACHE_TTL_SECONDS,
    AtlassianOpaqueTokenVerifier,
)


@pytest.mark.anyio
async def test_verify_token_returns_fastmcp_access_token() -> None:
    verifier = AtlassianOpaqueTokenVerifier(required_scopes=["read:jira-work"])

    async def _resources(_token: str) -> list[dict]:
        return [{"id": "cloud-1", "scopes": ["read:jira-work", "write:jira-work"]}]

    verifier._fetch_accessible_resources = _resources  # type: ignore[method-assign]

    token = await verifier.verify_token("opaque-token")

    assert isinstance(token, AccessToken)
    assert token is not None
    assert token.token == "opaque-token"
    assert "read:jira-work" in token.scopes
    assert token.client_id == "atlassian"


@pytest.mark.anyio
async def test_verify_token_returns_none_for_empty_token() -> None:
    verifier = AtlassianOpaqueTokenVerifier(required_scopes=[])

    token = await verifier.verify_token("")

    assert token is None


@pytest.mark.anyio
async def test_verify_token_expires_at_cache_ttl_future() -> None:
    """verify_token attaches an expiry based on the token cache TTL."""
    verifier = AtlassianOpaqueTokenVerifier(required_scopes=["read:jira-work"])

    async def _resources(_token: str) -> list[dict]:
        return [{"id": "cloud-1", "scopes": ["read:jira-work"]}]

    verifier._fetch_accessible_resources = _resources  # type: ignore[method-assign]

    before = int(time.time())
    token = await verifier.verify_token("opaque-token")
    after = int(time.time())

    assert token is not None
    assert token.expires_at is not None
    assert before + TOKEN_CACHE_TTL_SECONDS <= token.expires_at
    assert token.expires_at <= after + TOKEN_CACHE_TTL_SECONDS


@pytest.mark.anyio
async def test_verify_token_returns_none_when_required_scope_missing() -> None:
    verifier = AtlassianOpaqueTokenVerifier(required_scopes=["write:jira-work"])

    async def _resources(_token: str) -> list[dict]:
        return [{"id": "cloud-1", "scopes": ["read:jira-work"]}]

    verifier._fetch_accessible_resources = _resources  # type: ignore[method-assign]

    token = await verifier.verify_token("opaque-token")

    assert token is None


@pytest.mark.anyio
async def test_verify_token_returns_none_when_validation_fails() -> None:
    verifier = AtlassianOpaqueTokenVerifier(required_scopes=["read:jira-work"])

    async def _raise(_token: str) -> list[dict]:
        raise ValueError("validation failed")

    verifier._fetch_accessible_resources = _raise  # type: ignore[method-assign]

    token = await verifier.verify_token("opaque-token")

    assert token is None
