"""
AWS Athena Client — SQL query executor for data pipeline validation.

Executes queries against AWS Athena to validate data integrity,
schema compliance, and freshness of the Micropatient data pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Structured result from an Athena SQL query."""

    rows: list[dict[str, Any]]
    column_names: list[str]
    row_count: int
    execution_time_ms: float
    query: str
    status: str = "success"
    error: str | None = None


class AthenaClient:
    """
    AWS Athena SQL client for pipeline data validation.

    In mock mode, returns pre-defined results for testing.
    In live mode, executes actual Athena queries via pyathena.
    """

    def __init__(self, mode: str = "mock"):
        self.settings = get_settings()
        self.mode = mode
        self.database = self.settings.ATHENA_DATABASE

    def execute(self, query: str) -> QueryResult:
        """Execute SQL query against Athena (or mock)."""
        if self.mode == "mock":
            return self._mock_execute(query)
        return self._live_execute(query)

    # ── Pre-built Validation Queries ────────────

    def count_patients(self) -> QueryResult:
        return self.execute(f"SELECT COUNT(*) as total FROM {self.database}.patients")

    def check_null_columns(self, table: str, columns: list[str]) -> QueryResult:
        null_checks = ", ".join(
            f"SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) as {col}_nulls"
            for col in columns
        )
        return self.execute(
            f"SELECT COUNT(*) as total, {null_checks} FROM {self.database}.{table}"
        )

    def check_duplicates(self, table: str, key_column: str) -> QueryResult:
        return self.execute(f"""
            SELECT {key_column}, COUNT(*) as cnt
            FROM {self.database}.{table}
            GROUP BY {key_column}
            HAVING COUNT(*) > 1
        """)

    def check_data_freshness(self, table: str, timestamp_col: str = "updated_at") -> QueryResult:
        return self.execute(f"""
            SELECT
                MAX({timestamp_col}) as latest_record,
                MIN({timestamp_col}) as oldest_record,
                COUNT(*) as total_records,
                date_diff('hour', MAX({timestamp_col}), current_timestamp) as hours_since_update
            FROM {self.database}.{table}
        """)

    def get_conversation_stats(self) -> QueryResult:
        return self.execute(f"""
            SELECT
                COUNT(DISTINCT conversation_id) as total_conversations,
                AVG(total_tokens) as avg_tokens,
                AVG(total_cost_usd) as avg_cost,
                COUNT(DISTINCT patient_id) as unique_patients
            FROM {self.database}.conversations
        """)

    def get_latency_percentiles(self) -> QueryResult:
        return self.execute(f"""
            SELECT
                approx_percentile(latency_ms, 0.50) as p50,
                approx_percentile(latency_ms, 0.95) as p95,
                approx_percentile(latency_ms, 0.99) as p99,
                AVG(latency_ms) as avg_latency,
                MAX(latency_ms) as max_latency
            FROM {self.database}.messages
            WHERE role = 'ai'
        """)

    # ── Implementation ──────────────────────────

    def _mock_execute(self, query: str) -> QueryResult:
        """Return mock data for testing without AWS credentials."""
        query_lower = query.lower()

        if "count(*)" in query_lower and "patients" in query_lower:
            return QueryResult(
                rows=[{"total": 15234}],
                column_names=["total"],
                row_count=1,
                execution_time_ms=450.0,
                query=query,
            )
        if "null" in query_lower:
            return QueryResult(
                rows=[{"total": 15234, "email_nulls": 12, "phone_nulls": 45}],
                column_names=["total", "email_nulls", "phone_nulls"],
                row_count=1,
                execution_time_ms=820.0,
                query=query,
            )
        if "having count" in query_lower:
            return QueryResult(
                rows=[],  # No duplicates found
                column_names=["key", "cnt"],
                row_count=0,
                execution_time_ms=650.0,
                query=query,
            )
        if "hours_since_update" in query_lower:
            return QueryResult(
                rows=[{
                    "latest_record": "2025-10-15T14:30:00Z",
                    "oldest_record": "2024-01-01T00:00:00Z",
                    "total_records": 15234,
                    "hours_since_update": 2,
                }],
                column_names=["latest_record", "oldest_record", "total_records", "hours_since_update"],
                row_count=1,
                execution_time_ms=380.0,
                query=query,
            )
        if "percentile" in query_lower:
            return QueryResult(
                rows=[{
                    "p50": 245.0,
                    "p95": 1850.0,
                    "p99": 4200.0,
                    "avg_latency": 380.5,
                    "max_latency": 8900.0,
                }],
                column_names=["p50", "p95", "p99", "avg_latency", "max_latency"],
                row_count=1,
                execution_time_ms=1200.0,
                query=query,
            )
        if "conversation" in query_lower:
            return QueryResult(
                rows=[{
                    "total_conversations": 8542,
                    "avg_tokens": 1250.5,
                    "avg_cost": 0.035,
                    "unique_patients": 3210,
                }],
                column_names=["total_conversations", "avg_tokens", "avg_cost", "unique_patients"],
                row_count=1,
                execution_time_ms=950.0,
                query=query,
            )

        # Default mock
        return QueryResult(
            rows=[{"result": "mock_data"}],
            column_names=["result"],
            row_count=1,
            execution_time_ms=100.0,
            query=query,
        )

    def _live_execute(self, query: str) -> QueryResult:
        """Execute real Athena query via pyathena."""
        import time

        try:
            from pyathena import connect

            conn = connect(
                s3_staging_dir=self.settings.ATHENA_S3_OUTPUT,
                region_name=self.settings.AWS_REGION,
            )
            cursor = conn.cursor()

            start = time.perf_counter()
            cursor.execute(query)
            elapsed = (time.perf_counter() - start) * 1000

            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

            return QueryResult(
                rows=rows,
                column_names=columns,
                row_count=len(rows),
                execution_time_ms=elapsed,
                query=query,
            )
        except Exception as e:
            logger.error(f"Athena query failed: {e}")
            return QueryResult(
                rows=[],
                column_names=[],
                row_count=0,
                execution_time_ms=0,
                query=query,
                status="error",
                error=str(e),
            )
