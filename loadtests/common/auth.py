"""
Auth Helper — Shared authentication for load test users.

Handles login, token caching, and session management for
Locust HttpUser classes to avoid re-authenticating on every request.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Cached tokens to avoid re-authenticating under load
_token_cache: dict[str, str] = {}


def get_auth_headers(client, username: str, password: str) -> dict[str, str]:
    """
    Get authentication headers, using cached token if available.

    Args:
        client: Locust HttpUser's client instance.
        username: Login username.
        password: Login password.

    Returns:
        dict with Authorization header.
    """
    if username in _token_cache:
        return {"Authorization": f"Bearer {_token_cache[username]}"}

    try:
        response = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
            name="/api/v1/auth/login",
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("token", data.get("access_token", ""))
            if token:
                _token_cache[username] = token
                return {"Authorization": f"Bearer {token}"}
    except Exception as e:
        logger.warning(f"Auth failed for {username}: {e}")

    return {}


def clear_token_cache():
    """Clear all cached tokens."""
    _token_cache.clear()
