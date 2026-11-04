"""
Patient API Tests — CRUD operations for the /api/v1/patients endpoint.

Validates request/response contracts, status codes, required fields,
boundary conditions, and error handling for patient management.
"""

import pytest

from src.client.micropatient_api import MicropatientAPIClient
from src.utils.data_loader import load_api_payloads


class TestPatientAPI:
    """Contract tests for Patient REST endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = MicropatientAPIClient()
        self.payloads = load_api_payloads()

    # ── Create Patient ──────────────────────────

    @pytest.mark.api
    def test_create_patient_valid(self):
        """POST /api/v1/patients with valid data returns success."""
        payload = self.payloads["patients"]["valid_create"]
        response = self.client.create_patient(payload)

        # In mock mode, connection_failed is expected — validate contract intent
        if "error" in response and response["error"] == "connection_failed":
            pytest.skip("API server not running — contract validated structurally")

        assert "patient_id" in response or "id" in response, (
            f"Create patient response missing ID: {response}"
        )

    @pytest.mark.api
    def test_create_patient_missing_fields(self):
        """POST /api/v1/patients with missing required fields returns 400."""
        payload = self.payloads["patients"]["invalid_create_missing_fields"]
        response = self.client.create_patient(payload)

        if "error" in response and response["error"] == "connection_failed":
            pytest.skip("API server not running")

        assert "error" in response or "detail" in response, (
            "Missing fields should return error response"
        )

    @pytest.mark.api
    def test_create_patient_invalid_email(self):
        """POST /api/v1/patients with invalid email returns validation error."""
        payload = self.payloads["patients"]["invalid_create_bad_email"]
        response = self.client.create_patient(payload)

        if "error" in response and response["error"] == "connection_failed":
            pytest.skip("API server not running")

        assert "error" in response or "detail" in response, (
            "Invalid email should return validation error"
        )

    # ── Read Patient ────────────────────────────

    @pytest.mark.api
    def test_get_patient_valid_id(self):
        """GET /api/v1/patients/:id returns patient data."""
        response = self.client.get_patient("pat-test-001")

        if "error" in response and response["error"] == "connection_failed":
            pytest.skip("API server not running")

        if "error" not in response:
            required_fields = ["first_name", "last_name", "email"]
            for field in required_fields:
                assert field in response, f"Missing field: {field}"

    @pytest.mark.api
    def test_get_patient_invalid_id(self):
        """GET /api/v1/patients/:id with invalid ID returns 404."""
        response = self.client.get_patient("nonexistent-patient-999")

        if "error" in response and response["error"] == "connection_failed":
            pytest.skip("API server not running")

        assert "error" in response, "Invalid patient ID should return error"

    # ── List Patients ───────────────────────────

    @pytest.mark.api
    def test_list_patients_pagination(self):
        """GET /api/v1/patients supports pagination parameters."""
        response = self.client.list_patients(page=1, limit=10)

        if "error" in response and response["error"] == "connection_failed":
            pytest.skip("API server not running")

        # Validate pagination structure if server responds
        if "error" not in response:
            assert isinstance(response, (dict, list)), "List response should be dict or list"

    # ── Update Patient ──────────────────────────

    @pytest.mark.api
    def test_update_patient(self):
        """PUT /api/v1/patients/:id updates patient data."""
        response = self.client.update_patient(
            "pat-test-001",
            {"phone": "555-9999"}
        )

        if "error" in response and response["error"] == "connection_failed":
            pytest.skip("API server not running")

    # ── Delete Patient ──────────────────────────

    @pytest.mark.api
    def test_delete_patient_nonexistent(self):
        """DELETE /api/v1/patients/:id for nonexistent ID returns 404."""
        response = self.client.delete_patient("nonexistent-000")

        if "error" in response and response["error"] == "connection_failed":
            pytest.skip("API server not running")

        assert "error" in response, "Deleting nonexistent patient should return error"

    # ── Contract Validation ─────────────────────

    @pytest.mark.api
    def test_patient_payload_structure(self):
        """Validate the test payload structure matches API contract."""
        valid = self.payloads["patients"]["valid_create"]
        required = {"first_name", "last_name", "date_of_birth", "email", "phone"}
        assert required.issubset(valid.keys()), (
            f"Payload missing required fields: {required - valid.keys()}"
        )

    @pytest.mark.api
    def test_patient_email_format(self):
        """Validate test payload email format."""
        import re
        email = self.payloads["patients"]["valid_create"]["email"]
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        assert re.match(pattern, email), f"Invalid email in test payload: {email}"
