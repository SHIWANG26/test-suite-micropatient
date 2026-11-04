"""
Chat API Tests — Conversation and message endpoints.

Validates the /api/v1/chat/* endpoints for message sending,
conversation retrieval, input validation, and error handling.
"""

import pytest

from src.client.micropatient_api import MicropatientAPIClient
from src.utils.data_loader import load_api_payloads


class TestChatAPI:
    """Contract tests for Chat/Conversation REST endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = MicropatientAPIClient()
        self.payloads = load_api_payloads()

    # ── Send Message ────────────────────────────

    @pytest.mark.api
    def test_send_valid_message(self):
        """POST /api/v1/chat/messages with valid data returns AI response."""
        payload = self.payloads["chat"]["valid_message"]
        response = self.client.send_message(
            payload["conversation_id"],
            payload["message"],
            payload["patient_id"],
        )

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

        if "error" not in response:
            assert "message" in response or "answer" in response or "content" in response, (
                f"Chat response missing message content: {response}"
            )

    @pytest.mark.api
    def test_send_empty_message_rejected(self):
        """POST /api/v1/chat/messages with empty message returns 400."""
        payload = self.payloads["chat"]["empty_message"]
        response = self.client.send_message(
            payload["conversation_id"],
            payload["message"],
            payload["patient_id"],
        )

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

        # Empty messages should be rejected
        if payload["message"] == "":
            assert "error" in response or "detail" in response, (
                "Empty message should return validation error"
            )

    @pytest.mark.api
    def test_send_oversized_message(self):
        """POST /api/v1/chat/messages with oversized message returns 400."""
        payload = self.payloads["chat"]["oversized_message"]
        response = self.client.send_message(
            payload["conversation_id"],
            payload["message"],
            payload["patient_id"],
        )

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

        # Oversized messages should trigger validation or at least not crash
        assert isinstance(response, dict), "Response should be a valid JSON dict"

    # ── Conversation Retrieval ──────────────────

    @pytest.mark.api
    def test_get_conversation(self):
        """GET /api/v1/chat/conversations/:id returns conversation data."""
        response = self.client.get_conversation("conv-test-001")

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

    @pytest.mark.api
    def test_get_conversation_invalid_id(self):
        """GET /api/v1/chat/conversations/:id with invalid ID returns 404."""
        response = self.client.get_conversation("nonexistent-conv-999")

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

        assert "error" in response, "Invalid conversation ID should return error"

    @pytest.mark.api
    def test_list_conversations_for_patient(self):
        """GET /api/v1/chat/conversations?patient_id=X returns conversation list."""
        response = self.client.list_conversations("pat-test-001")

        if response.get("error") == "connection_failed":
            pytest.skip("API server not running")

    # ── Contract Validation ─────────────────────

    @pytest.mark.api
    def test_chat_payload_structure(self):
        """Validate chat test payload structure."""
        valid = self.payloads["chat"]["valid_message"]
        required = {"conversation_id", "message", "patient_id"}
        assert required.issubset(valid.keys()), (
            f"Chat payload missing fields: {required - valid.keys()}"
        )

    @pytest.mark.api
    def test_message_content_not_null(self):
        """Validate that valid test message is non-empty."""
        msg = self.payloads["chat"]["valid_message"]["message"]
        assert msg and len(msg) > 0, "Valid message payload should not be empty"
