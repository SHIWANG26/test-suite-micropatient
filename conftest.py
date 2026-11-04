"""
Root conftest.py — Global pytest fixtures shared across ALL test suites.

Provides environment configuration, API client, and test markers
available to evals/, safety/, and tests/ directories.
"""

import pytest

from config.settings import get_settings
from src.client.llm_client import MicropatientLLMClient
from src.client.micropatient_api import MicropatientAPIClient


@pytest.fixture(scope="session")
def settings():
    """Global settings singleton."""
    return get_settings()


@pytest.fixture(scope="session")
def api_client(settings):
    """Pre-configured API client for Micropatient REST endpoints."""
    return MicropatientAPIClient(
        base_url=settings.MICROPATIENT_BASE_URL,
        timeout=30,
    )


@pytest.fixture(scope="session")
def llm_client():
    """Mock LLM client — no API keys needed for test runs."""
    return MicropatientLLMClient(mode="mock")
