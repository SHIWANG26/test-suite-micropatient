"""
Locust Entry Point — Micropatient Load Test Suite.

Imports all user scenarios so Locust discovers them automatically.
Traffic distribution is controlled by the `weight` attribute on each class:
  - PatientBrowsingUser: weight=2 (20%)
  - ChatConversationUser: weight=5 (50%)
  - APIStressUser: weight=3 (30%)

Usage:
  # Headless (CI):
  locust -f loadtests/locustfile.py --headless -u 100 -r 10 --run-time 5m

  # Web UI:
  locust -f loadtests/locustfile.py
  # Then open http://localhost:8089
"""

# Import all scenario classes — Locust auto-discovers HttpUser subclasses
from loadtests.scenarios.patient_browsing import PatientBrowsingUser  # noqa: F401
from loadtests.scenarios.chat_conversation import ChatConversationUser  # noqa: F401
from loadtests.scenarios.api_stress import APIStressUser  # noqa: F401
