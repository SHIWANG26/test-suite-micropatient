"""
Data Loader — Utilities for loading test datasets from JSON/YAML files.

Provides typed access to golden datasets, safety test data, and API payloads.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_json(file_path: str | Path) -> dict[str, Any]:
    """Load and parse a JSON file."""
    path = Path(file_path)
    if not path.is_absolute():
        path = DATA_DIR / path
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_rag_test_cases() -> list[dict[str, Any]]:
    """Load the curated RAG golden dataset test cases."""
    data = load_json("golden_dataset/rag_test_cases.json")
    return data.get("test_cases", [])


def load_multi_turn_conversations() -> list[dict[str, Any]]:
    """Load multi-turn conversation test data."""
    data = load_json("golden_dataset/multi_turn_conversations.json")
    return data.get("conversations", [])


def load_prompt_injections() -> list[dict[str, Any]]:
    """Load prompt injection attack test cases."""
    data = load_json("safety/prompt_injections.json")
    return data.get("test_cases", [])


def load_jailbreak_attempts() -> list[dict[str, Any]]:
    """Load jailbreak attempt test cases."""
    data = load_json("safety/jailbreak_attempts.json")
    return data.get("test_cases", [])


def load_pii_samples() -> dict[str, Any]:
    """Load PII leakage test cases and regex patterns."""
    return load_json("safety/pii_samples.json")


def load_blocked_topics() -> list[dict[str, Any]]:
    """Load blocked topic test cases."""
    data = load_json("safety/blocked_topics.json")
    return data.get("test_cases", [])


def load_api_payloads() -> dict[str, Any]:
    """Load API test request/response payloads."""
    return load_json("api/test_payloads.json")


def load_thresholds() -> dict[str, Any]:
    """Load metric thresholds from YAML config."""
    import yaml

    threshold_path = DATA_DIR.parent / "config" / "thresholds.yaml"
    with open(threshold_path, encoding="utf-8") as f:
        return yaml.safe_load(f)
