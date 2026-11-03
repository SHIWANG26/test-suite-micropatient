"""
Shared pytest fixtures for the LLM evaluation suite.

Provides pre-loaded golden dataset test cases, LLM client instances,
metrics tracker, and DeepEval test case factory.
"""

import uuid

import pytest

from config.settings import get_settings
from src.client.llm_client import MicropatientLLMClient
from src.utils.data_loader import load_rag_test_cases
from src.utils.metrics_tracker import EvalRun, MetricsTracker


@pytest.fixture(scope="session")
def settings():
    """Shared settings instance."""
    return get_settings()


@pytest.fixture(scope="session")
def llm_client():
    """Mock LLM client for evaluation — no API keys needed."""
    return MicropatientLLMClient(mode="mock")


@pytest.fixture(scope="session")
def golden_dataset():
    """Load the curated golden dataset once per session."""
    return load_rag_test_cases()


@pytest.fixture(scope="session")
def eval_run():
    """Create a new evaluation run for tracking metrics."""
    import os

    return EvalRun(
        run_id=str(uuid.uuid4())[:8],
        model_version="mock-gpt-4o",
        commit_sha=os.getenv("GITHUB_SHA", "local-dev"),
    )


@pytest.fixture(scope="session")
def metrics_tracker():
    """Metrics tracker for persisting evaluation results."""
    return MetricsTracker()
