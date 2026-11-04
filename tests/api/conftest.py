"""
Shared fixtures for REST API tests.

Provides authenticated API clients, test payloads, and
response validation helpers.
"""

import pytest

from config.settings import get_settings
from src.client.micropatient_api import MicropatientAPIClient
from src.utils.data_loader import load_api_payloads


@pytest.fixture(scope="session")
def api_client():
    """API client for test execution."""
    settings = get_settings()
    return MicropatientAPIClient(
        base_url=settings.MICROPATIENT_BASE_URL,
        timeout=30,
    )


@pytest.fixture(scope="session")
def auth_client():
    """Authenticated API client with admin credentials."""
    settings = get_settings()
    client = MicropatientAPIClient(
        base_url=settings.MICROPATIENT_BASE_URL,
        timeout=30,
    )
    client.login(settings.TEST_ADMIN_USERNAME, settings.TEST_ADMIN_PASSWORD)
    return client


@pytest.fixture(scope="session")
def payloads():
    """Load test payloads from data/api/test_payloads.json."""
    return load_api_payloads()


def assert_error_response(response: dict, expected_status: str | None = None):
    """Helper to validate error response structure."""
    assert "error" in response or "detail" in response or "message" in response, (
        f"Error response missing error field: {response}"
    )
    if expected_status:
        assert response.get("error", "").startswith(expected_status), (
            f"Expected status {expected_status}, got: {response}"
        )


def assert_valid_entity(entity: dict, required_fields: list[str]):
    """Helper to validate entity has required fields."""
    for field in required_fields:
        assert field in entity, f"Missing required field '{field}' in entity: {entity}"
