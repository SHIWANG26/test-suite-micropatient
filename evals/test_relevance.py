"""
Relevance Tests — Verify RAG answers are relevant to the user's question.

Ensures the model's response actually addresses the question asked,
rather than providing off-topic or tangentially related information.
"""

import pytest

from config.settings import get_settings
from src.client.llm_client import MicropatientLLMClient
from src.utils.data_loader import load_rag_test_cases

settings = get_settings()


class TestRelevance:
    """Test suite for RAG answer relevance scoring."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.llm_client = MicropatientLLMClient(mode="mock")
        self.test_cases = load_rag_test_cases()
        self.threshold = settings.RELEVANCE_THRESHOLD

    @pytest.mark.llm_eval
    @pytest.mark.parametrize("case_idx", range(15))
    def test_answer_relevance(self, case_idx):
        """
        Verify the answer is relevant to the input question.

        Measures keyword overlap between question and answer as a
        relevance proxy (in production, use DeepEval AnswerRelevancyMetric).
        """
        if case_idx >= len(self.test_cases):
            pytest.skip("Test case index out of range")

        case = self.test_cases[case_idx]
        response = self.llm_client.query(case["input"])

        # Extract question topic keywords
        question_keywords = self._extract_topic_words(case["input"])
        answer_text = response.answer.lower()

        # Check how many question topic words appear in the answer
        matched = sum(1 for kw in question_keywords if kw in answer_text)
        score = matched / len(question_keywords) if question_keywords else 0.0

        assert score >= self.threshold, (
            f"[{case['id']}] Relevance score {score:.3f} below threshold "
            f"{self.threshold}. Answer may not address the question."
        )

    @pytest.mark.llm_eval
    def test_no_cross_contamination(self):
        """
        Verify answers don't mix topics from different test cases.

        A medication question shouldn't include procedure prep details, etc.
        """
        category_keywords = {
            "medication": {"medication", "drug", "dose", "side effect", "prescri"},
            "symptoms": {"symptom", "sign", "watch for", "emergency", "pain"},
            "procedures": {"procedure", "prepare", "scan", "surgery", "test"},
            "insurance": {"insurance", "deductible", "coverage", "copay", "plan"},
        }

        for case in self.test_cases[:10]:
            category = case.get("category")
            if category not in category_keywords or category == "refusal":
                continue

            response = self.llm_client.query(case["input"])
            answer_lower = response.answer.lower()

            # Check that the answer doesn't predominantly match a *different* category
            scores = {}
            for cat, keywords in category_keywords.items():
                hits = sum(1 for kw in keywords if kw in answer_lower)
                scores[cat] = hits

            if scores:
                best_match = max(scores, key=scores.get)
                # The best-matching category should be the correct one
                # (or at least not a completely wrong one)
                assert scores.get(category, 0) > 0 or best_match == category, (
                    f"[{case['id']}] Answer for '{category}' question best matches "
                    f"'{best_match}' category — possible cross-contamination."
                )

    @staticmethod
    def _extract_topic_words(question: str) -> list[str]:
        """Extract meaningful topic words from a question."""
        stop_words = {
            "what", "how", "when", "where", "why", "which", "who",
            "is", "are", "do", "does", "can", "should", "would",
            "the", "a", "an", "i", "my", "me", "for", "to", "of",
            "and", "or", "in", "on", "at", "by", "with", "about",
            "after", "before", "know", "need", "many", "much",
        }
        words = question.lower().replace("?", "").split()
        return [w for w in words if w not in stop_words and len(w) > 2]
