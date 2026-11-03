"""
LLM Client — Wrapper for interacting with the Micropatient AI model.

Used by evaluation and safety tests to send queries and collect responses
including retrieval context, latency, and token usage metadata.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Structured response from the LLM including evaluation metadata."""

    answer: str
    retrieval_context: list[str] = field(default_factory=list)
    model: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    raw_response: dict[str, Any] = field(default_factory=dict)


class MicropatientLLMClient:
    """
    Client for the Micropatient RAG-powered AI endpoint.

    In production, this calls the actual /api/v1/chat/completions endpoint.
    For local testing, it returns mock responses from the golden dataset.
    """

    def __init__(self, mode: str = "mock"):
        self.settings = get_settings()
        self.mode = mode
        self._mock_responses: dict[str, LLMResponse] = {}
        if mode == "mock":
            self._load_mock_responses()

    def query(self, question: str, context: list[str] | None = None) -> LLMResponse:
        """
        Send a question to the Micropatient AI and return structured response.

        Args:
            question: The user's input query.
            context: Optional retrieval context (used in evaluation).

        Returns:
            LLMResponse with answer, retrieval context, and metadata.
        """
        start = time.perf_counter()

        if self.mode == "mock":
            response = self._mock_query(question, context)
        else:
            response = self._live_query(question, context)

        response.latency_ms = (time.perf_counter() - start) * 1000
        return response

    def _mock_query(
        self, question: str, context: list[str] | None = None
    ) -> LLMResponse:
        """Return a mock response for testing without API calls."""
        # Check if we have a pre-loaded mock response
        for key, resp in self._mock_responses.items():
            if key.lower() in question.lower():
                return LLMResponse(
                    answer=resp.answer,
                    retrieval_context=context or resp.retrieval_context,
                    model="mock-gpt-4o",
                    tokens_used=150,
                )

        # Default mock response
        return LLMResponse(
            answer=(
                "Based on the available medical information, I'd recommend "
                "consulting with your healthcare provider for personalized advice "
                "regarding your specific situation."
            ),
            retrieval_context=context or [
                "General medical reference: Always consult a licensed healthcare "
                "provider for medical advice, diagnosis, or treatment."
            ],
            model="mock-gpt-4o",
            tokens_used=80,
        )

    def _live_query(
        self, question: str, context: list[str] | None = None
    ) -> LLMResponse:
        """Send a real query to the Micropatient API."""
        import requests

        try:
            response = requests.post(
                f"{self.settings.MICROPATIENT_BASE_URL}/api/v1/chat/completions",
                json={"message": question, "context": context or []},
                headers={"Authorization": f"Bearer {self.settings.OPENAI_API_KEY}"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                answer=data.get("answer", ""),
                retrieval_context=data.get("retrieval_context", []),
                model=data.get("model", "unknown"),
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                tool_calls=data.get("tool_calls", []),
                raw_response=data,
            )
        except Exception as e:
            logger.error(f"Live query failed: {e}")
            return LLMResponse(
                answer=f"Error: {e}",
                model="error",
            )

    def _load_mock_responses(self) -> None:
        """Pre-load mock responses from the golden dataset."""
        import json
        from pathlib import Path

        dataset_path = Path(__file__).parent.parent.parent / "data" / "golden_dataset" / "rag_test_cases.json"
        if not dataset_path.exists():
            logger.warning(f"Golden dataset not found at {dataset_path}")
            return

        with open(dataset_path) as f:
            data = json.load(f)

        for case in data.get("test_cases", []):
            # Index by first significant words of the question
            key = " ".join(case["input"].split()[:5]).lower()
            self._mock_responses[key] = LLMResponse(
                answer=case["expected_output"],
                retrieval_context=case.get("retrieval_context", []),
            )
        logger.info(f"Loaded {len(self._mock_responses)} mock responses")
