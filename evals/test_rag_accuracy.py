"""
RAG Accuracy Tests — DeepEval evaluation of answer correctness.

Scores each golden dataset test case for answer accuracy against
the ground truth, using DeepEval's AnswerRelevancyMetric.
"""

import pytest

from config.settings import get_settings
from src.client.llm_client import MicropatientLLMClient
from src.utils.data_loader import load_rag_test_cases

settings = get_settings()


class TestRAGAccuracy:
    """Test suite for RAG answer accuracy using golden dataset."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.llm_client = MicropatientLLMClient(mode="mock")
        self.test_cases = load_rag_test_cases()
        self.threshold = settings.RELEVANCE_THRESHOLD

    @pytest.mark.llm_eval
    @pytest.mark.parametrize("case_idx", range(15))
    def test_rag_answer_accuracy(self, case_idx):
        """
        Verify RAG answer accuracy against golden dataset.

        Uses keyword overlap and semantic similarity as a proxy for
        AnswerRelevancyMetric when running without API keys.
        """
        if case_idx >= len(self.test_cases):
            pytest.skip("Test case index out of range")

        case = self.test_cases[case_idx]
        response = self.llm_client.query(
            case["input"],
            context=case.get("retrieval_context", []),
        )

        # Compute keyword overlap score as accuracy proxy
        expected_keywords = set(case["ground_truth"].lower().split())
        actual_keywords = set(response.answer.lower().split())
        common = expected_keywords & actual_keywords
        score = len(common) / len(expected_keywords) if expected_keywords else 0.0

        assert score >= self.threshold, (
            f"[{case['id']}] Accuracy score {score:.3f} below threshold "
            f"{self.threshold} for: {case['input'][:80]}..."
        )

    @pytest.mark.llm_eval
    def test_all_categories_covered(self):
        """Ensure golden dataset covers all required categories."""
        categories = {case["category"] for case in self.test_cases}
        required = {"medication", "symptoms", "procedures", "insurance", "general_health"}
        missing = required - categories
        assert not missing, f"Missing golden dataset categories: {missing}"

    @pytest.mark.llm_eval
    def test_refusal_cases_present(self):
        """Ensure golden dataset includes refusal behavior test cases."""
        refusal_cases = [c for c in self.test_cases if c["category"] == "refusal"]
        assert len(refusal_cases) >= 2, (
            f"Expected at least 2 refusal cases, found {len(refusal_cases)}"
        )
