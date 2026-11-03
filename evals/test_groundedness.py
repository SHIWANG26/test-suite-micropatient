"""
Groundedness / Faithfulness Tests — Verify answers are grounded in retrieval context.

Ensures the LLM does not fabricate information beyond what's in the
retrieved documents, using keyword overlap as a faithfulness proxy.
"""

import pytest

from config.settings import get_settings
from src.client.llm_client import MicropatientLLMClient
from src.utils.data_loader import load_rag_test_cases

settings = get_settings()


class TestGroundedness:
    """Test suite for RAG answer groundedness / faithfulness."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.llm_client = MicropatientLLMClient(mode="mock")
        self.test_cases = load_rag_test_cases()
        self.threshold = settings.GROUNDEDNESS_THRESHOLD

    @pytest.mark.llm_eval
    @pytest.mark.parametrize("case_idx", range(15))
    def test_answer_groundedness(self, case_idx):
        """
        Verify that the answer is grounded in the retrieval context.

        Measures what fraction of answer sentences can be traced back
        to the retrieval context content.
        """
        if case_idx >= len(self.test_cases):
            pytest.skip("Test case index out of range")

        case = self.test_cases[case_idx]

        # Skip refusal test cases — they intentionally deviate from context
        if case.get("category") == "refusal":
            pytest.skip("Refusal cases are not expected to be grounded")

        response = self.llm_client.query(
            case["input"],
            context=case.get("retrieval_context", []),
        )

        # Compute groundedness as keyword overlap with retrieval context
        context_text = " ".join(case.get("retrieval_context", [])).lower()
        context_words = set(context_text.split())

        answer_words = set(response.answer.lower().split())
        # Filter out common stop words for better signal
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "shall",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "and",
            "but", "or", "nor", "not", "so", "yet", "both", "either",
            "neither", "each", "every", "all", "any", "few", "more",
            "most", "other", "some", "such", "no", "only", "own", "same",
            "than", "too", "very", "just", "because", "if", "when", "that",
            "this", "these", "those", "it", "its", "i", "you", "your",
        }

        answer_content_words = answer_words - stop_words
        grounded_words = answer_content_words & context_words
        score = len(grounded_words) / len(answer_content_words) if answer_content_words else 0.0

        assert score >= self.threshold, (
            f"[{case['id']}] Groundedness score {score:.3f} below threshold "
            f"{self.threshold}. Answer may contain fabricated information."
        )

    @pytest.mark.llm_eval
    def test_no_external_claims(self):
        """
        Verify that answers don't introduce medical claims not present in context.

        Checks the first 5 non-refusal test cases for claims about
        specific numbers/dosages not found in the retrieval context.
        """
        non_refusal = [c for c in self.test_cases if c.get("category") != "refusal"]

        for case in non_refusal[:5]:
            response = self.llm_client.query(
                case["input"],
                context=case.get("retrieval_context", []),
            )
            context_text = " ".join(case.get("retrieval_context", [])).lower()

            # Extract numeric claims from answer
            import re
            answer_numbers = set(re.findall(r"\b\d+(?:\.\d+)?(?:%|mg|ml|hours?|days?|weeks?)?\b", response.answer.lower()))
            context_numbers = set(re.findall(r"\b\d+(?:\.\d+)?(?:%|mg|ml|hours?|days?|weeks?)?\b", context_text))

            unsupported_numbers = answer_numbers - context_numbers
            # Allow small tolerance for common numbers
            common_numbers = {"1", "2", "3", "4", "5", "10", "100"}
            truly_unsupported = unsupported_numbers - common_numbers

            assert len(truly_unsupported) <= 2, (
                f"[{case['id']}] Found potentially fabricated numeric claims: {truly_unsupported}"
            )
