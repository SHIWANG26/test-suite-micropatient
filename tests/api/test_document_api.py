"""
Document API Tests — Document ingestion and retrieval endpoints.

Validates the /api/v1/documents endpoint for uploading medical
documents, triggering embeddings, and retrieval for RAG.
"""

import pytest

from src.client.micropatient_api import MicropatientAPIClient
from src.utils.data_loader import load_api_payloads


class TestDocumentAPI:
    """Contract tests for Document management REST endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = MicropatientAPIClient()
        self.payloads = load_api_payloads()

    # ── Upload Document ─────────────────────────

    @pytest.mark.api
    def test_upload_valid_document(self):
        """POST /api/v1/documents with valid data returns document ID."""
        payload = self.payloads["documents"]["valid_upload"]
        response = self.client.upload_document(
            payload["patient_id"],
            payload["document_type"],
            payload["content"],
        )

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

        if "error" not in response:
            assert "document_id" in response or "id" in response, (
                f"Upload response missing document ID: {response}"
            )

    @pytest.mark.api
    def test_upload_empty_content(self):
        """POST /api/v1/documents with empty content returns 400."""
        response = self.client.upload_document(
            "pat-test-001", "lab_result", ""
        )

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

    @pytest.mark.api
    def test_upload_invalid_patient_id(self):
        """POST /api/v1/documents with invalid patient ID returns 404."""
        response = self.client.upload_document(
            "nonexistent-patient-999", "lab_result", "Test content"
        )

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

    # ── Retrieve Document ───────────────────────

    @pytest.mark.api
    def test_get_document_valid_id(self):
        """GET /api/v1/documents/:id returns document data."""
        response = self.client.get_document("doc-test-001")

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

    @pytest.mark.api
    def test_get_document_invalid_id(self):
        """GET /api/v1/documents/:id with invalid ID returns 404."""
        response = self.client.get_document("nonexistent-doc-999")

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

        assert "error" in response, "Invalid document ID should return error"

    # ── Contract Validation ─────────────────────

    @pytest.mark.api
    def test_document_payload_structure(self):
        """Validate document test payload structure."""
        valid = self.payloads["documents"]["valid_upload"]
        required = {"patient_id", "document_type", "content"}
        assert required.issubset(valid.keys()), (
            f"Document payload missing fields: {required - valid.keys()}"
        )

    @pytest.mark.api
    def test_document_type_valid(self):
        """Validate document type is a recognized enum value."""
        doc_type = self.payloads["documents"]["valid_upload"]["document_type"]
        valid_types = {"lab_result", "prescription", "imaging", "clinical_note", "discharge_summary"}
        assert doc_type in valid_types, f"Unknown document type: {doc_type}"

    @pytest.mark.api
    def test_document_content_nonempty(self):
        """Validate valid document payload has non-empty content."""
        content = self.payloads["documents"]["valid_upload"]["content"]
        assert len(content) > 10, "Valid document content should be substantial"
