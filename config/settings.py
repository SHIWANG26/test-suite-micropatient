"""
Centralized configuration using Pydantic Settings.

Loads values from .env files and environment variables, with sensible defaults
for local development. All thresholds and endpoints are configured here so that
tests never contain hardcoded secrets or magic numbers.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Application Under Test ──────────────────
    MICROPATIENT_BASE_URL: str = "http://localhost:8000"
    MICROPATIENT_UI_URL: str = "http://localhost:3000"

    # ── Auth Credentials ────────────────────────
    TEST_ADMIN_USERNAME: str = "admin@micropatient.dev"
    TEST_ADMIN_PASSWORD: str = "test-admin-password"
    TEST_DOCTOR_USERNAME: str = "doctor@micropatient.dev"
    TEST_DOCTOR_PASSWORD: str = "test-doctor-password"
    TEST_PATIENT_USERNAME: str = "patient@micropatient.dev"
    TEST_PATIENT_PASSWORD: str = "test-patient-password"

    # ── LLM / OpenAI ───────────────────────────
    OPENAI_API_KEY: str = "sk-mock-key-for-testing"
    EVAL_MODEL: str = "gpt-4o-2024-11-20"
    EVAL_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── LangSmith ──────────────────────────────
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "micropatient-evals"
    LANGCHAIN_TRACING_V2: bool = False

    # ── DeepEval ───────────────────────────────
    DEEPEVAL_API_KEY: str = ""

    # ── AWS ─────────────────────────────────────
    AWS_REGION: str = "us-east-1"
    ATHENA_DATABASE: str = "micropatient_prod"
    ATHENA_S3_OUTPUT: str = "s3://micropatient-athena-results/"

    # ── Metric Thresholds ──────────────────────
    FAITHFULNESS_THRESHOLD: float = 0.8
    RELEVANCE_THRESHOLD: float = 0.75
    GROUNDEDNESS_THRESHOLD: float = 0.8
    HALLUCINATION_THRESHOLD: float = 0.15
    CONTEXT_PRECISION_THRESHOLD: float = 0.7
    CONTEXT_RECALL_THRESHOLD: float = 0.7

    # ── Performance Thresholds ─────────────────
    LATENCY_P95_THRESHOLD_MS: int = 2000
    LATENCY_P99_THRESHOLD_MS: int = 5000
    ERROR_RATE_THRESHOLD: float = 0.01

    # ── Environment ────────────────────────────
    ENV: str = "staging"

    @property
    def is_ci(self) -> bool:
        """Check if running in CI environment."""
        import os
        return os.getenv("CI", "false").lower() == "true"

    @property
    def data_dir(self) -> Path:
        return ROOT_DIR / "data"

    @property
    def reports_dir(self) -> Path:
        reports = ROOT_DIR / "reports"
        reports.mkdir(exist_ok=True)
        return reports


@lru_cache
def get_settings() -> Settings:
    """Return cached singleton Settings instance."""
    return Settings()
