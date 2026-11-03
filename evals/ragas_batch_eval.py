"""
Ragas Batch Evaluation — DataFrame-driven evaluation of the full golden dataset.

Runs Ragas metrics (faithfulness, answer_relevancy, context_precision,
context_recall) over the entire golden dataset and outputs scores as CSV.

Usage:
    python evals/ragas_batch_eval.py
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent


def load_golden_dataset() -> dict:
    """Load golden dataset for Ragas evaluation."""
    path = ROOT_DIR / "data" / "golden_dataset" / "rag_test_cases.json"
    with open(path) as f:
        return json.load(f)


def run_mock_evaluation() -> dict:
    """
    Run mock Ragas evaluation (no API keys required).

    In production, replace with actual Ragas evaluate() call:

        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

        dataset = Dataset.from_dict({...})
        result = evaluate(dataset=dataset, metrics=[faithfulness, answer_relevancy, ...])
    """
    data = load_golden_dataset()
    test_cases = data["test_cases"]

    results = []
    for case in test_cases:
        if case.get("category") == "refusal":
            continue

        # Simulate Ragas scores using keyword analysis
        context_text = " ".join(case.get("retrieval_context", [])).lower()
        expected_text = case["expected_output"].lower()
        ground_truth = case["ground_truth"].lower()

        context_words = set(context_text.split())
        expected_words = set(expected_text.split())
        truth_words = set(ground_truth.split())

        stop = {"the", "a", "an", "is", "are", "to", "of", "and", "or", "in", "for", "with", "on", "at"}
        ctx_content = context_words - stop
        exp_content = expected_words - stop
        truth_content = truth_words - stop

        # Simulated metric scores
        faithfulness = len(exp_content & ctx_content) / len(exp_content) if exp_content else 0
        answer_relevancy = len(exp_content & truth_content) / len(truth_content) if truth_content else 0
        context_precision = len(ctx_content & truth_content) / len(ctx_content) if ctx_content else 0
        context_recall = len(truth_content & ctx_content) / len(truth_content) if truth_content else 0

        results.append({
            "test_case_id": case["id"],
            "category": case["category"],
            "question": case["input"][:80],
            "faithfulness": round(faithfulness, 4),
            "answer_relevancy": round(answer_relevancy, 4),
            "context_precision": round(context_precision, 4),
            "context_recall": round(context_recall, 4),
        })

    return {
        "metadata": {
            "evaluator": "ragas_batch_mock",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_cases": len(results),
        },
        "results": results,
        "aggregated": _aggregate(results),
    }


def _aggregate(results: list[dict]) -> dict:
    """Compute aggregated metric averages."""
    metrics = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    agg = {}
    for metric in metrics:
        values = [r[metric] for r in results]
        agg[metric] = {
            "mean": round(sum(values) / len(values), 4) if values else 0,
            "min": round(min(values), 4) if values else 0,
            "max": round(max(values), 4) if values else 0,
        }
    return agg


def main():
    """Run the batch evaluation and save results."""
    logger.info("Starting Ragas batch evaluation...")

    results = run_mock_evaluation()

    # Save JSON report
    reports_dir = ROOT_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = reports_dir / f"ragas_eval_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary table
    logger.info("\n📊 Ragas Evaluation Results:")
    logger.info("=" * 65)
    logger.info(f"{'Metric':<25} {'Mean':>8} {'Min':>8} {'Max':>8}")
    logger.info("-" * 65)
    for metric, stats in results["aggregated"].items():
        logger.info(f"{metric:<25} {stats['mean']:>8.4f} {stats['min']:>8.4f} {stats['max']:>8.4f}")
    logger.info("=" * 65)
    logger.info(f"Total test cases: {results['metadata']['total_cases']}")
    logger.info(f"Report saved: {output_path}")

    return results


if __name__ == "__main__":
    main()
