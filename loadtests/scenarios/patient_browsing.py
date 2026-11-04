"""
Patient Browsing Scenario — Simulates patient browsing behavior.

Models patients logging in, viewing their records, checking
appointments, and browsing the portal — 20% of total traffic.
"""

from locust import task, between

from loadtests.scenarios.api_stress import BaseAPIUser


class PatientBrowsingUser(BaseAPIUser):
    """
    Simulates a patient browsing the Micropatient portal.

    Weighted at 20% of total load. Represents read-heavy traffic
    patterns: viewing records, checking appointments, reading documents.
    """

    weight = 2
    wait_time = between(2, 5)

    @task(5)
    def view_patient_profile(self):
        """Patient views their own profile."""
        self.client.get(
            "/api/v1/patients/pat-load-001",
            headers=self.auth_headers,
            name="/api/v1/patients/:id",
        )

    @task(4)
    def list_conversations(self):
        """Patient views their conversation history."""
        self.client.get(
            "/api/v1/chat/conversations",
            params={"patient_id": "pat-load-001"},
            headers=self.auth_headers,
            name="/api/v1/chat/conversations",
        )

    @task(3)
    def view_conversation(self):
        """Patient reads a specific past conversation."""
        self.client.get(
            "/api/v1/chat/conversations/conv-load-001",
            headers=self.auth_headers,
            name="/api/v1/chat/conversations/:id",
        )

    @task(2)
    def view_document(self):
        """Patient views a medical document."""
        self.client.get(
            "/api/v1/documents/doc-load-001",
            headers=self.auth_headers,
            name="/api/v1/documents/:id",
        )

    @task(1)
    def health_check(self):
        """Hit the health endpoint."""
        self.client.get("/api/v1/health", name="/api/v1/health")
