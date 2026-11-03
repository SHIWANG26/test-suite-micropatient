"""
Hallucination Tracking Tests — Monitor hallucination rate across releases.

Tracks the hallucination rate per evaluation run and flags regressions
relative to the previous release baseline.
"""

import uuid

import pytest

from config.settings import get_settings
from src.client.llm_client import MicropatientLLMClient
from src.utils.data_loader import load_rag_test_cases
from src.utils.metrics_tracker import EvalRun, MetricsTracker

settings = get_settings()


class TestHallucinationTracking:
    """Track and compare hallucination rates across releases."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.llm_client = MicropatientLLMClient(mode="mock")
        self.test_cases = [
            c for c in load_rag_test_cases() if c.get("category") != "refusal"
        ]
        self.threshold = settings.HALLUCINATION_THRESHOLD
        self.tracker = MetricsTracker(history_file="eval_history_test.json")

    @pytest.mark.llm_eval
    def test_hallucination_rate_below_threshold(self):
        """
        Verify the overall hallucination rate is below the configured threshold.

        Hallucination is measured as the proportion of answer content words
        NOT found in the retrieval context (proxy for real hallucination metric).
        """
        hallucination_scores = []

        for case in self.test_cases:
            response = self.llm_client.query(
                case["input"],
                context=case.get("retrieval_context", []),
            )

            context_text = " ".join(case.get("retrieval_context", [])).lower()
            context_words = set(context_text.split())

            answer_words = set(response.answer.lower().split())
            stop_words = {
                "the", "a", "an", "is", "are", "was", "to", "of", "in",
                "for", "on", "with", "at", "by", "and", "or", "but",
                "not", "be", "this", "that", "it", "as", "from", "your",
                "you", "can", "may", "should", "will", "if", "such",
            }
            content_words = answer_words - stop_words
            unsupported = content_words - context_words
            hallucination_rate = (
                len(unsupported) / len(content_words) if content_words else 0.0
            )
            hallucination_scores.append(hallucination_rate)

        avg_hallucination = (
            sum(hallucination_scores) / len(hallucination_scores)
            if hallucination_scores
            else 0.0
        )

        assert avg_hallucination <= self.threshold, (
            f"Average hallucination rate {avg_hallucination:.3f} exceeds "
            f"threshold {self.threshold}. Review model outputs for fabricated content."
        )

    @pytest.mark.llm_eval
    def test_record_and_compare_hallucination(self):
        """
        Record current hallucination metrics and compare against previous run.

        This test always passes but logs warnings if regressions are detected.
        Regressions are surfaced in CI logs and the evaluation report.
        """
        run = EvalRun(
            run_id=str(uuid.uuid4())[:8],
            model_version="mock-gpt-4o",
        )

        for case in self.test_cases[:5]:
            response = self.llm_client.query(
                case["input"],
                context=case.get("retrieval_context", []),
            )

            # Compute mock scores
            context_text = " ".join(case.get("retrieval_context", [])).lower()
            answer_lower = response.answer.lower()

            context_words = set(context_text.split())
            answer_words = set(answer_lower.split()) - {"the", "a", "is", "to", "of", "and"}
            grounded = answer_words & context_words
            faithfulness = len(grounded) / len(answer_words) if answer_words else 0.0

            run.add_score("faithfulness", faithfulness, settings.FAITHFULNESS_THRESHOLD, case["id"])
            run.add_score("hallucination", 1.0 - faithfulness, self.threshold, case["id"])

        self.tracker.save_run(run)
        comparison = self.tracker.compare_runs()

        if comparison and comparison.get("has_regressions"):
            import warnings
            for reg in comparison["regressions"]:
                warnings.warn(
                    f"⚠️  REGRESSION: {reg['metric']} dropped from "
                    f"{reg['previous']:.3f} → {reg['current']:.3f} "
                    f"(Δ {reg['delta']:+.3f})",
                    UserWarning,
                    stacklevel=2,
                )

    @pytest.mark.llm_eval
    def test_no_complete_fabrication(self):
        """
        Verify no test case produces a completely hallucinated response.

        A response where <20% of content words appear in context is
        considered a complete fabrication.
        """
        for case in self.test_cases:
            response = self.llm_client.query(
                case["input"],
                context=case.get("retrieval_context", []),
            )

            context_text = " ".join(case.get("retrieval_context", [])).lower()
            context_words = set(context_text.split())
            answer_words = set(response.answer.lower().split())
            stop_words = {"the", "a", "an", "is", "are", "to", "of", "and", "or", "in", "for"}
            content_words = answer_words - stop_words

            grounded = content_words & context_words
            grounding_rate = len(grounded) / len(content_words) if content_words else 0.0

            assert grounding_rate >= 0.2, (
                f"[{case['id']}] Complete fabrication detected! "
                f"Only {grounding_rate:.1%} of content words found in context."
            )
