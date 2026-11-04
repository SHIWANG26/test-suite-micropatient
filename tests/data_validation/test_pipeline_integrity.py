"""
Pipeline Integrity Tests — Validate data flowing through the Micropatient pipeline.

Runs SQL queries against AWS Athena (or mock) to verify row counts,
null percentages, duplicates, data freshness, and latency metrics.
"""

import pytest

from config.settings import get_settings
from src.client.athena_client import AthenaClient
from src.utils.data_loader import load_thresholds


class TestPipelineIntegrity:
    """Data pipeline validation using SQL / AWS Athena queries."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.athena = AthenaClient(mode="mock")
        self.settings = get_settings()
        self.thresholds = load_thresholds().get("data_validation", {})

    # ── Row Count Checks ────────────────────────

    @pytest.mark.data_validation
    def test_patients_table_not_empty(self):
        """Verify patients table has records."""
        result = self.athena.count_patients()
        assert result.status == "success", f"Query failed: {result.error}"
        total = result.rows[0]["total"]
        assert total > 0, "Patients table is empty — pipeline may have failed"

    @pytest.mark.data_validation
    def test_conversations_have_data(self):
        """Verify conversations table has records."""
        result = self.athena.get_conversation_stats()
        assert result.status == "success"
        total = result.rows[0]["total_conversations"]
        assert total > 0, "No conversations found — check ingestion pipeline"

    # ── Null Checks ─────────────────────────────

    @pytest.mark.data_validation
    def test_patient_null_rate_below_threshold(self):
        """Verify null rate in critical patient columns is acceptable."""
        result = self.athena.check_null_columns(
            "patients", ["email", "phone"]
        )
        assert result.status == "success"

        total = result.rows[0]["total"]
        threshold = self.thresholds.get("null_threshold_percent", 1.0)

        for col in ["email", "phone"]:
            nulls = result.rows[0].get(f"{col}_nulls", 0)
            null_pct = (nulls / total * 100) if total > 0 else 0
            assert null_pct <= threshold, (
                f"Column '{col}' has {null_pct:.2f}% nulls (threshold: {threshold}%)"
            )

    # ── Duplicate Checks ────────────────────────

    @pytest.mark.data_validation
    def test_no_duplicate_patient_ids(self):
        """Verify no duplicate patient IDs exist."""
        result = self.athena.check_duplicates("patients", "patient_id")
        assert result.status == "success"
        assert result.row_count == 0, (
            f"Found {result.row_count} duplicate patient IDs: {result.rows[:5]}"
        )

    @pytest.mark.data_validation
    def test_no_duplicate_conversation_ids(self):
        """Verify no duplicate conversation IDs exist."""
        result = self.athena.check_duplicates("conversations", "conversation_id")
        assert result.status == "success"
        assert result.row_count == 0, (
            f"Found {result.row_count} duplicate conversation IDs"
        )

    # ── Data Freshness ──────────────────────────

    @pytest.mark.data_validation
    def test_patient_data_freshness(self):
        """Verify patient data has been updated within acceptable window."""
        result = self.athena.check_data_freshness("patients")
        assert result.status == "success"

        max_hours = self.thresholds.get("staleness_hours", 24)
        hours_since = result.rows[0].get("hours_since_update", 0)
        assert hours_since <= max_hours, (
            f"Patient data is {hours_since}h old (threshold: {max_hours}h)"
        )

    # ── Latency & Cost Monitoring ───────────────

    @pytest.mark.data_validation
    def test_latency_within_sla(self):
        """Verify AI response latency percentiles are within SLA."""
        result = self.athena.get_latency_percentiles()
        assert result.status == "success"

        p95 = result.rows[0]["p95"]
        p99 = result.rows[0]["p99"]

        assert p95 <= self.settings.LATENCY_P95_THRESHOLD_MS, (
            f"P95 latency {p95}ms exceeds threshold {self.settings.LATENCY_P95_THRESHOLD_MS}ms"
        )
        assert p99 <= self.settings.LATENCY_P99_THRESHOLD_MS, (
            f"P99 latency {p99}ms exceeds threshold {self.settings.LATENCY_P99_THRESHOLD_MS}ms"
        )

    @pytest.mark.data_validation
    def test_conversation_cost_reasonable(self):
        """Verify average conversation cost is within budget."""
        result = self.athena.get_conversation_stats()
        assert result.status == "success"

        avg_cost = result.rows[0]["avg_cost"]
        # $0.50 per conversation is a reasonable upper bound for GPT-4o
        assert avg_cost < 0.50, (
            f"Average conversation cost ${avg_cost:.3f} exceeds $0.50 budget"
        )

    # ── Query Performance ───────────────────────

    @pytest.mark.data_validation
    def test_query_execution_performance(self):
        """Verify Athena queries execute within acceptable time."""
        result = self.athena.count_patients()
        assert result.execution_time_ms < 30000, (
            f"Query took {result.execution_time_ms}ms — exceeds 30s limit"
        )
