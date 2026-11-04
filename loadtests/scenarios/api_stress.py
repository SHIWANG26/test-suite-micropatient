"""
API Stress Scenario — Exercises all API endpoints under load.

Models mixed API traffic from admin and doctor users performing
CRUD operations — 30% of total traffic.
"""

from locust import HttpUser, between, task

from loadtests.common.auth import get_auth_headers


class BaseAPIUser(HttpUser):
    """
    Base Locust user with authentication support.

    All scenario user classes inherit from this to get
    shared auth logic and lifecycle management.
    """

    abstract = True
    wait_time = between(1, 3)

    def on_start(self):
        """Authenticate on user session start."""
        self.auth_headers = get_auth_headers(
            self.client,
            "doctor@micropatient.dev",
            "test-doctor-password",
        )

    def on_stop(self):
        """Cleanup on user session end."""
        pass


class APIStressUser(BaseAPIUser):
    """
    Simulates admin/doctor API operations under load.

    Weighted at 30% of total load. Exercises CRUD endpoints,
    document uploads, and patient management operations.
    """

    weight = 3
    wait_time = between(1, 4)

    # ── Patient CRUD ────────────────────────────

    @task(5)
    def list_patients(self):
        """GET /api/v1/patients — list all patients."""
        self.client.get(
            "/api/v1/patients",
            params={"page": 1, "limit": 20},
            headers=self.auth_headers,
            name="/api/v1/patients",
        )

    @task(3)
    def get_patient(self):
        """GET /api/v1/patients/:id — get specific patient."""
        self.client.get(
            "/api/v1/patients/pat-load-001",
            headers=self.auth_headers,
            name="/api/v1/patients/:id",
        )

    @task(2)
    def create_patient(self):
        """POST /api/v1/patients — create a patient."""
        import random
        self.client.post(
            "/api/v1/patients",
            json={
                "first_name": f"LoadTest{random.randint(1, 9999)}",
                "last_name": "User",
                "date_of_birth": "1990-01-01",
                "email": f"load{random.randint(1, 9999)}@test.com",
                "phone": "555-0000",
            },
            headers=self.auth_headers,
            name="/api/v1/patients [POST]",
        )

    # ── Document Operations ─────────────────────

    @task(2)
    def upload_document(self):
        """POST /api/v1/documents — upload a medical document."""
        self.client.post(
            "/api/v1/documents",
            json={
                "patient_id": "pat-load-001",
                "document_type": "lab_result",
                "content": "Load test document — CBC results: WBC 7.0, RBC 4.5",
            },
            headers=self.auth_headers,
            name="/api/v1/documents [POST]",
        )

    @task(3)
    def get_document(self):
        """GET /api/v1/documents/:id — retrieve a document."""
        self.client.get(
            "/api/v1/documents/doc-load-001",
            headers=self.auth_headers,
            name="/api/v1/documents/:id",
        )

    # ── Health & Auth ───────────────────────────

    @task(4)
    def health_check(self):
        """GET /api/v1/health — hit health endpoint."""
        self.client.get("/api/v1/health", name="/api/v1/health")

    @task(1)
    def login(self):
        """POST /api/v1/auth/login — re-authenticate."""
        self.client.post(
            "/api/v1/auth/login",
            json={
                "username": "doctor@micropatient.dev",
                "password": "test-doctor-password",
            },
            name="/api/v1/auth/login",
        )
