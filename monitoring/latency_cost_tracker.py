"""
Latency & Cost Tracker — Monitors LLM response latency and token costs.

Queries CloudWatch or mock data to track API response times and
LLM token costs, generating alerts when thresholds are breached.

Usage:
    python monitoring/latency_cost_tracker.py
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class LatencyCostSnapshot:
    """Point-in-time snapshot of latency and cost metrics."""

    timestamp: str
    api_latency_p50_ms: float
    api_latency_p95_ms: float
    api_latency_p99_ms: float
    llm_latency_avg_ms: float
    total_tokens_1h: int
    cost_usd_1h: float
    error_rate: float
    alerts: list[str]


def collect_metrics(mode: str = "mock") -> LatencyCostSnapshot:
    """
    Collect latency and cost metrics from CloudWatch or mock data.

    Args:
        mode: "mock" for testing, "live" for real CloudWatch queries.

    Returns:
        LatencyCostSnapshot with current metrics.
    """
    if mode == "mock":
        return _mock_metrics()
    return _live_metrics()


def _mock_metrics() -> LatencyCostSnapshot:
    """Generate mock metrics for testing."""
    alerts = []

    # Simulated metrics
    p95 = 1850.0
    p99 = 4200.0
    cost = 12.45
    error_rate = 0.008

    # Check thresholds
    if p95 > 2000:
        alerts.append(f"⚠️ P95 latency {p95}ms exceeds 2000ms threshold")
    if p99 > 5000:
        alerts.append(f"🚨 P99 latency {p99}ms exceeds 5000ms threshold")
    if cost > 50:
        alerts.append(f"💰 Hourly LLM cost ${cost:.2f} exceeds $50 budget")
    if error_rate > 0.01:
        alerts.append(f"❌ Error rate {error_rate:.1%} exceeds 1% threshold")

    return LatencyCostSnapshot(
        timestamp=datetime.now(UTC).isoformat(),
        api_latency_p50_ms=245.0,
        api_latency_p95_ms=p95,
        api_latency_p99_ms=p99,
        llm_latency_avg_ms=380.5,
        total_tokens_1h=125000,
        cost_usd_1h=cost,
        error_rate=error_rate,
        alerts=alerts,
    )


def _live_metrics() -> LatencyCostSnapshot:
    """Collect real metrics from AWS CloudWatch."""
    try:
        import boto3

        boto3.client("cloudwatch", region_name="us-east-1")

        # Query CloudWatch metrics...
        # (Simplified — production code would use get_metric_statistics)

        logger.info("Live CloudWatch metrics collection not yet implemented")
        return _mock_metrics()

    except Exception as e:
        logger.error(f"CloudWatch query failed: {e}")
        return _mock_metrics()


def main():
    """Run the latency/cost tracker and output results."""
    logger.info("📊 Collecting Micropatient latency & cost metrics...")

    snapshot = collect_metrics(mode="mock")

    logger.info(f"\n{'=' * 60}")
    logger.info("  Micropatient — Latency & Cost Report")
    logger.info(f"  {snapshot.timestamp}")
    logger.info(f"{'='*60}")
    logger.info(f"  API Latency  P50: {snapshot.api_latency_p50_ms:>8.1f} ms")
    logger.info(f"               P95: {snapshot.api_latency_p95_ms:>8.1f} ms")
    logger.info(f"               P99: {snapshot.api_latency_p99_ms:>8.1f} ms")
    logger.info(f"  LLM Latency  Avg: {snapshot.llm_latency_avg_ms:>8.1f} ms")
    logger.info(f"  Tokens (1h):      {snapshot.total_tokens_1h:>8,}")
    logger.info(f"  Cost (1h):        ${snapshot.cost_usd_1h:>7.2f}")
    logger.info(f"  Error Rate:       {snapshot.error_rate:>8.3%}")
    logger.info(f"{'='*60}")

    if snapshot.alerts:
        logger.warning("\n🚨 ALERTS:")
        for alert in snapshot.alerts:
            logger.warning(f"  {alert}")
    else:
        logger.info("\n✅ All metrics within thresholds")

    # Save snapshot
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / "latency_cost_latest.json"
    with open(report_path, "w") as f:
        json.dump(asdict(snapshot), f, indent=2)
    logger.info(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    main()
