"""
Environment-specific configuration profiles.

Each profile holds the target host URLs and environment-specific overrides
so tests can seamlessly switch between dev, staging, and production.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentConfig:
    """Immutable environment profile."""

    name: str
    api_base_url: str
    ui_base_url: str
    athena_database: str
    timeout_seconds: int = 30
    retries: int = 3
    verify_ssl: bool = True


ENVIRONMENTS: dict[str, EnvironmentConfig] = {
    "dev": EnvironmentConfig(
        name="dev",
        api_base_url="http://localhost:8000",
        ui_base_url="http://localhost:3000",
        athena_database="micropatient_dev",
        timeout_seconds=60,
        retries=1,
        verify_ssl=False,
    ),
    "staging": EnvironmentConfig(
        name="staging",
        api_base_url="https://staging-api.micropatient.dev",
        ui_base_url="https://staging.micropatient.dev",
        athena_database="micropatient_staging",
        timeout_seconds=30,
        retries=3,
        verify_ssl=True,
    ),
    "production": EnvironmentConfig(
        name="production",
        api_base_url="https://api.micropatient.dev",
        ui_base_url="https://app.micropatient.dev",
        athena_database="micropatient_prod",
        timeout_seconds=15,
        retries=2,
        verify_ssl=True,
    ),
}


def get_environment(env_name: str = "staging") -> EnvironmentConfig:
    """Return the environment configuration for the given name."""
    env_name = env_name.lower()
    if env_name not in ENVIRONMENTS:
        raise ValueError(
            f"Unknown environment '{env_name}'. "
            f"Choose from: {', '.join(ENVIRONMENTS.keys())}"
        )
    return ENVIRONMENTS[env_name]
