"""
LoginPage — Page Object for the Micropatient login/authentication page.

Encapsulates login form locators and authentication workflow methods.
Uses web-first locators (roles, labels) for resilience.
"""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import get_settings
from tests.ui.pages.base_page import BasePage


class LoginPage(BasePage):
    """Page object for the Micropatient login page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.settings = get_settings()

        # ── Locators ────────────────────────────
        self.username_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Sign In")
        self.error_message = page.locator("[data-testid='login-error']")
        self.forgot_password_link = page.get_by_role("link", name="Forgot password")
        self.logo = page.locator("[data-testid='app-logo']")
        self.remember_me_checkbox = page.get_by_label("Remember me")

    # ── Actions ─────────────────────────────────

    def load(self) -> None:
        """Navigate to the login page."""
        self.navigate(f"{self.settings.MICROPATIENT_UI_URL}/login")

    def login(self, username: str, password: str) -> None:
        """Perform login with given credentials."""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def login_as_doctor(self) -> None:
        """Login with default doctor test credentials."""
        self.login(
            self.settings.TEST_DOCTOR_USERNAME,
            self.settings.TEST_DOCTOR_PASSWORD,
        )

    def login_as_patient(self) -> None:
        """Login with default patient test credentials."""
        self.login(
            self.settings.TEST_PATIENT_USERNAME,
            self.settings.TEST_PATIENT_PASSWORD,
        )

    def login_as_admin(self) -> None:
        """Login with default admin test credentials."""
        self.login(
            self.settings.TEST_ADMIN_USERNAME,
            self.settings.TEST_ADMIN_PASSWORD,
        )

    # ── Assertions ──────────────────────────────

    def verify_login_page_loaded(self) -> None:
        """Assert the login page elements are visible."""
        self.expect_visible(self.username_input)
        self.expect_visible(self.password_input)
        self.expect_visible(self.login_button)

    def verify_error_displayed(self, expected_text: str | None = None) -> None:
        """Assert login error message is visible."""
        self.expect_visible(self.error_message)
        if expected_text:
            self.expect_text(self.error_message, expected_text)

    def verify_redirected_to_dashboard(self) -> None:
        """Assert successful login redirects to dashboard."""
        self.wait_for_url("**/dashboard**")
        self.expect_url_contains("dashboard")
