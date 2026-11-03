"""
Micropatient API Client — HTTP wrapper for the system under test.

Provides authenticated REST calls to all Micropatient endpoints.
Used by API tests, load tests, and integration tests.
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import get_settings

logger = logging.getLogger(__name__)


class MicropatientAPIClient:
    """Reusable HTTP client for the Micropatient REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = 30,
        retries: int = 3,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.MICROPATIENT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self._token: str | None = None

        # Configure retry strategy
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    # ── Authentication ──────────────────────────
    def login(self, username: str, password: str) -> dict[str, Any]:
        """Authenticate and store JWT token for subsequent requests."""
        response = self._post("/api/v1/auth/login", json={
            "username": username,
            "password": password,
        })
        if response.get("token"):
            self._token = response["token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self._token}"
            })
        return response

    def logout(self) -> None:
        """Clear authentication token."""
        self._token = None
        self.session.headers.pop("Authorization", None)

    # ── Patient Endpoints ───────────────────────
    def create_patient(self, patient_data: dict) -> dict:
        return self._post("/api/v1/patients", json=patient_data)

    def get_patient(self, patient_id: str) -> dict:
        return self._get(f"/api/v1/patients/{patient_id}")

    def list_patients(self, page: int = 1, limit: int = 20) -> dict:
        return self._get("/api/v1/patients", params={"page": page, "limit": limit})

    def update_patient(self, patient_id: str, data: dict) -> dict:
        return self._put(f"/api/v1/patients/{patient_id}", json=data)

    def delete_patient(self, patient_id: str) -> dict:
        return self._delete(f"/api/v1/patients/{patient_id}")

    # ── Chat / Conversation Endpoints ───────────
    def send_message(self, conversation_id: str, message: str, patient_id: str) -> dict:
        return self._post("/api/v1/chat/messages", json={
            "conversation_id": conversation_id,
            "message": message,
            "patient_id": patient_id,
        })

    def get_conversation(self, conversation_id: str) -> dict:
        return self._get(f"/api/v1/chat/conversations/{conversation_id}")

    def list_conversations(self, patient_id: str) -> dict:
        return self._get(f"/api/v1/chat/conversations", params={"patient_id": patient_id})

    # ── Document Endpoints ──────────────────────
    def upload_document(self, patient_id: str, doc_type: str, content: str) -> dict:
        return self._post("/api/v1/documents", json={
            "patient_id": patient_id,
            "document_type": doc_type,
            "content": content,
        })

    def get_document(self, document_id: str) -> dict:
        return self._get(f"/api/v1/documents/{document_id}")

    # ── Health Check ────────────────────────────
    def health_check(self) -> dict:
        return self._get("/api/v1/health")

    # ── Internal HTTP Methods ───────────────────
    def _get(self, path: str, **kwargs) -> dict:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs) -> dict:
        return self._request("POST", path, **kwargs)

    def _put(self, path: str, **kwargs) -> dict:
        return self._request("PUT", path, **kwargs)

    def _delete(self, path: str, **kwargs) -> dict:
        return self._request("DELETE", path, **kwargs)

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Execute HTTP request with logging and error handling."""
        url = f"{self.base_url}{path}"
        logger.debug(f"{method} {url}")

        try:
            response = self.session.request(
                method, url, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection failed: {url}")
            return {"error": "connection_failed", "url": url}
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out: {url}")
            return {"error": "timeout", "url": url}
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP {e.response.status_code}: {url}")
            try:
                return e.response.json()
            except ValueError:
                return {"error": f"http_{e.response.status_code}", "detail": str(e)}
