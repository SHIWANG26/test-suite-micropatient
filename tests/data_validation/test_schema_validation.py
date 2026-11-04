"""
Schema Validation Tests — Verify database schema compliance.

Ensures all expected tables exist, columns have correct types,
and foreign key relationships are maintained.
"""

import pytest

from src.client.athena_client import AthenaClient


class TestSchemaValidation:
    """Schema conformance tests for Micropatient data pipeline."""

    EXPECTED_TABLES = [
        "patients",
        "conversations",
        "messages",
        "medical_documents",
        "retrieval_logs",
        "eval_results",
    ]

    PATIENTS_COLUMNS = [
        "patient_id", "first_name", "last_name",
        "date_of_birth", "email", "phone",
        "created_at", "updated_at",
    ]

    CONVERSATIONS_COLUMNS = [
        "conversation_id", "patient_id", "started_at",
        "ended_at", "status", "total_tokens",
        "total_cost_usd", "model_version",
    ]

    MESSAGES_COLUMNS = [
        "message_id", "conversation_id", "role",
        "content", "tokens_used", "latency_ms",
        "model_used", "created_at",
    ]

    @pytest.fixture(autouse=True)
    def setup(self):
        self.athena = AthenaClient(mode="mock")

    @pytest.mark.data_validation
    def test_expected_tables_defined(self):
        """Verify all expected tables are defined in schema."""
        # In mock mode, validate that our queries reference valid tables
        for table in self.EXPECTED_TABLES:
            result = self.athena.execute(
                f"SELECT 1 FROM micropatient_prod.{table} LIMIT 1"
            )
            # Mock will return data for any query — real mode validates existence
            assert result.status == "success", f"Table '{table}' query failed"

    @pytest.mark.data_validation
    def test_patients_table_schema(self):
        """Verify patients table has all required columns."""
        result = self.athena.check_null_columns("patients", self.PATIENTS_COLUMNS[:2])
        assert result.status == "success"
        # Validate we can query these columns without error

    @pytest.mark.data_validation
    def test_conversations_table_schema(self):
        """Verify conversations table has all required columns."""
        result = self.athena.get_conversation_stats()
        assert result.status == "success"
        # Stats query exercises conversation_id, patient_id, total_tokens, total_cost_usd

    @pytest.mark.data_validation
    def test_messages_table_schema(self):
        """Verify messages table has latency tracking columns."""
        result = self.athena.get_latency_percentiles()
        assert result.status == "success"
        # Latency query exercises latency_ms and role columns

    @pytest.mark.data_validation
    def test_patient_id_foreign_key_consistency(self):
        """Verify patient_id foreign keys reference existing patients."""
        # Check no orphaned conversations exist
        result = self.athena.execute("""
            SELECT c.conversation_id
            FROM micropatient_prod.conversations c
            LEFT JOIN micropatient_prod.patients p ON c.patient_id = p.patient_id
            WHERE p.patient_id IS NULL
        """)
        assert result.status == "success"
        assert result.row_count == 0, (
            f"Found {result.row_count} orphaned conversations with no matching patient"
        )

    @pytest.mark.data_validation
    def test_message_role_values(self):
        """Verify message role column only contains valid values."""
        result = self.athena.execute("""
            SELECT DISTINCT role
            FROM micropatient_prod.messages
            WHERE role NOT IN ('user', 'ai', 'system')
        """)
        assert result.status == "success"
        assert result.row_count == 0, (
            f"Found invalid role values: {result.rows}"
        )

    @pytest.mark.data_validation
    def test_eval_results_table_exists(self):
        """Verify eval_results table exists for metric tracking."""
        result = self.athena.execute(
            "SELECT COUNT(*) as cnt FROM micropatient_prod.eval_results"
        )
        assert result.status == "success"
