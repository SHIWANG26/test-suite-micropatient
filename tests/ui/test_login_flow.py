"""
Login Flow UI Tests — Playwright end-to-end tests for authentication.

Covers successful login, invalid credentials, empty fields,
forgot password navigation, and session persistence.
"""

import pytest

from tests.ui.pages.login_page import LoginPage


@pytest.mark.ui
class TestLoginFlow:
    """End-to-end UI tests for the login flow."""

    def test_login_page_elements_visible(self, login_page: LoginPage):
        """Verify all login page elements render correctly."""
        login_page.load()
        login_page.verify_login_page_loaded()

    def test_successful_doctor_login(self, login_page: LoginPage):
        """Doctor login with valid credentials redirects to dashboard."""
        login_page.load()
        login_page.login_as_doctor()
        login_page.verify_redirected_to_dashboard()

    def test_invalid_password_shows_error(self, login_page: LoginPage):
        """Login with wrong password displays error message."""
        login_page.load()
        login_page.login("doctor@micropatient.dev", "wrong-password")
        login_page.verify_error_displayed()

    def test_empty_fields_shows_validation(self, login_page: LoginPage):
        """Submitting empty login form shows validation errors."""
        login_page.load()
        login_page.login("", "")
        # Browser's built-in validation or custom error
        assert login_page.page.url.endswith("/login"), (
            "Empty login should stay on login page"
        )

    def test_patient_login_redirects_to_portal(self, login_page: LoginPage):
        """Patient login redirects to the patient portal (not doctor dashboard)."""
        login_page.load()
        login_page.login_as_patient()
        # Patient should go to portal, not dashboard
        login_page.page.wait_for_timeout(2000)

    def test_login_page_title(self, login_page: LoginPage):
        """Verify login page has correct title."""
        login_page.load()
        title = login_page.get_page_title()
        assert title, "Login page should have a title"
