"""
Metrics Tracker — Records and compares evaluation scores across releases.

Tracks hallucination rate, faithfulness, and other LLM metrics over time
to detect regressions before deployment.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"


@dataclass
class EvalScore:
    """A single metric score from an evaluation run."""

    metric_name: str
    score: float
    threshold: float
    passed: bool
    test_case_id: str = ""
    details: str = ""


@dataclass
class EvalRun:
    """An entire evaluation run containing multiple metric scores."""

    run_id: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    model_version: str = ""
    commit_sha: str = ""
    scores: list[EvalScore] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def all_passed(self) -> bool:
        return all(s.passed for s in self.scores)

    @property
    def pass_rate(self) -> float:
        if not self.scores:
            return 0.0
        return sum(1 for s in self.scores if s.passed) / len(self.scores)

    @property
    def hallucination_rate(self) -> float:
        """Calculate average hallucination score across all test cases."""
        hall_scores = [
            s.score for s in self.scores if s.metric_name == "hallucination"
        ]
        return sum(hall_scores) / len(hall_scores) if hall_scores else 0.0

    def add_score(self, metric_name: str, score: float, threshold: float, test_case_id: str = "") -> None:
        """Add a metric score to this run."""
        self.scores.append(EvalScore(
            metric_name=metric_name,
            score=score,
            threshold=threshold,
            passed=score >= threshold if metric_name != "hallucination" else score <= threshold,
            test_case_id=test_case_id,
        ))

    def compute_summary(self) -> dict[str, Any]:
        """Compute aggregate summary statistics."""
        metrics: dict[str, list[float]] = {}
        for s in self.scores:
            metrics.setdefault(s.metric_name, []).append(s.score)

        self.summary = {
            metric: {
                "mean": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "count": len(scores),
            }
            for metric, scores in metrics.items()
        }
        self.summary["overall_pass_rate"] = self.pass_rate
        self.summary["hallucination_rate"] = self.hallucination_rate
        return self.summary


class MetricsTracker:
    """Persists evaluation results and compares across releases."""

    def __init__(self, history_file: str = "eval_history.json"):
        REPORTS_DIR.mkdir(exist_ok=True)
        self.history_file = REPORTS_DIR / history_file
        self.history: list[dict] = self._load_history()

    def save_run(self, run: EvalRun) -> None:
        """Save an evaluation run to the history file."""
        run.compute_summary()
        self.history.append(asdict(run))
        self._persist()
        logger.info(
            f"Saved eval run {run.run_id}: "
            f"pass_rate={run.pass_rate:.1%}, "
            f"hallucination_rate={run.hallucination_rate:.3f}"
        )

    def get_latest_run(self) -> dict | None:
        """Return the most recent evaluation run."""
        return self.history[-1] if self.history else None

    def get_previous_run(self) -> dict | None:
        """Return the second-most-recent run for comparison."""
        return self.history[-2] if len(self.history) >= 2 else None

    def compare_runs(self) -> dict[str, Any] | None:
        """Compare latest run against previous run to detect regressions."""
        latest = self.get_latest_run()
        previous = self.get_previous_run()
        if not latest or not previous:
            return None

        comparison: dict[str, Any] = {"regressions": [], "improvements": []}
        latest_summary = latest.get("summary", {})
        prev_summary = previous.get("summary", {})

        for metric in latest_summary:
            if metric in ("overall_pass_rate", "hallucination_rate"):
                continue
            if metric not in prev_summary:
                continue

            latest_mean = latest_summary[metric].get("mean", 0)
            prev_mean = prev_summary[metric].get("mean", 0)
            delta = latest_mean - prev_mean

            entry = {
                "metric": metric,
                "current": round(latest_mean, 4),
                "previous": round(prev_mean, 4),
                "delta": round(delta, 4),
            }
            if delta < -0.05:  # >5% drop is a regression
                comparison["regressions"].append(entry)
            elif delta > 0.05:
                comparison["improvements"].append(entry)

        # Special handling for hallucination rate (lower is better)
        if "hallucination_rate" in latest_summary and "hallucination_rate" in prev_summary:
            curr_hr = latest_summary["hallucination_rate"]
            prev_hr = prev_summary["hallucination_rate"]
            if curr_hr > prev_hr + 0.02:  # 2% increase is a regression
                comparison["regressions"].append({
                    "metric": "hallucination_rate",
                    "current": round(curr_hr, 4),
                    "previous": round(prev_hr, 4),
                    "delta": round(curr_hr - prev_hr, 4),
                })

        comparison["has_regressions"] = len(comparison["regressions"]) > 0
        return comparison

    def _load_history(self) -> list[dict]:
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return []

    def _persist(self) -> None:
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2, default=str)
