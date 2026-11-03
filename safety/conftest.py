"""
Shared fixtures for AI safety tests.
"""

import pytest

from src.client.llm_client import MicropatientLLMClient
from src.utils.data_loader import (
    load_blocked_topics,
    load_jailbreak_attempts,
    load_pii_samples,
    load_prompt_injections,
)


@pytest.fixture(scope="session")
def llm_client():
    return MicropatientLLMClient(mode="mock")


@pytest.fixture(scope="session")
def injection_cases():
    return load_prompt_injections()


@pytest.fixture(scope="session")
def jailbreak_cases():
    return load_jailbreak_attempts()


@pytest.fixture(scope="session")
def pii_data():
    return load_pii_samples()


@pytest.fixture(scope="session")
def blocked_topic_cases():
    return load_blocked_topics()
