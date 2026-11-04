"""
PatientPortalPage — Page Object for the Patient self-service portal.

Encapsulates patient record viewing, appointment scheduling,
document access, and profile management.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import get_settings
from tests.ui.pages.base_page import BasePage


class PatientPortalPage(BasePage):
    """Page object for the Patient self-service portal."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.settings = get_settings()

        # ── Locators ────────────────────────────
        self.welcome_banner = page.locator("[data-testid='welcome-banner']")
        self.appointments_section = page.locator("[data-testid='appointments']")
        self.documents_section = page.locator("[data-testid='documents']")
        self.profile_section = page.locator("[data-testid='profile']")
        self.book_appointment_btn = page.get_by_role("button", name="Book Appointment")
        self.chat_with_ai_btn = page.get_by_role("button", name="Chat with AI")
        self.lab_results_link = page.get_by_role("link", name="Lab Results")
        self.prescription_link = page.get_by_role("link", name="Prescriptions")
        self.upcoming_appointments = page.locator("[data-testid='upcoming-appointments']")
        self.medical_records = page.locator("[data-testid='medical-records']")

    # ── Actions ─────────────────────────────────

    def load(self) -> None:
        """Navigate to the patient portal."""
        self.navigate(f"{self.settings.MICROPATIENT_UI_URL}/portal")

    def click_book_appointment(self) -> None:
        """Click book appointment button."""
        self.click(self.book_appointment_btn)

    def click_chat_with_ai(self) -> None:
        """Navigate to AI chat from portal."""
        self.click(self.chat_with_ai_btn)

    def click_lab_results(self) -> None:
        """Navigate to lab results section."""
        self.click(self.lab_results_link)

    def click_prescriptions(self) -> None:
        """Navigate to prescriptions section."""
        self.click(self.prescription_link)

    # ── Assertions ──────────────────────────────

    def verify_portal_loaded(self) -> None:
        """Assert patient portal elements are visible."""
        self.expect_visible(self.welcome_banner)

    def verify_appointments_visible(self) -> None:
        """Assert appointments section is visible."""
        self.expect_visible(self.appointments_section)

    def verify_documents_visible(self) -> None:
        """Assert documents section is visible."""
        self.expect_visible(self.documents_section)

    def verify_no_pii_visible(self) -> None:
        """Assert no raw PII patterns are visible on page."""
        import re
        page_content = self.page.content()
        ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        matches = re.findall(ssn_pattern, page_content)
        assert len(matches) == 0, f"SSN pattern found on page: {matches}"
