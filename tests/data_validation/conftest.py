"""
Shared fixtures for data validation tests.
"""

import pytest

from src.client.athena_client import AthenaClient


@pytest.fixture(scope="session")
def athena():
    """Mock Athena client for data validation testing."""
    return AthenaClient(mode="mock")
