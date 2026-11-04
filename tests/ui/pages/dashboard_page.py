"""
DashboardPage — Page Object for the Doctor's dashboard.

Encapsulates widgets, patient lists, and analytics display for
the main dashboard view after doctor login.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import get_settings
from tests.ui.pages.base_page import BasePage


class DashboardPage(BasePage):
    """Page object for the Doctor Dashboard."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.settings = get_settings()

        # ── Locators ────────────────────────────
        self.page_title = page.locator("h1")
        self.patient_list = page.locator("[data-testid='patient-list']")
        self.search_input = page.get_by_placeholder("Search patients")
        self.new_patient_btn = page.get_by_role("button", name="New Patient")
        self.stats_widget = page.locator("[data-testid='stats-widget']")
        self.recent_conversations = page.locator("[data-testid='recent-conversations']")
        self.nav_menu = page.locator("nav")
        self.logout_btn = page.get_by_role("button", name="Logout")
        self.profile_avatar = page.locator("[data-testid='profile-avatar']")
        self.notification_badge = page.locator("[data-testid='notification-badge']")

    # ── Actions ─────────────────────────────────

    def load(self) -> None:
        """Navigate directly to the dashboard."""
        self.navigate(f"{self.settings.MICROPATIENT_UI_URL}/dashboard")

    def search_patient(self, query: str) -> None:
        """Search for a patient by name or ID."""
        self.fill(self.search_input, query)
        self.page.keyboard.press("Enter")

    def click_new_patient(self) -> None:
        """Click the 'New Patient' button."""
        self.click(self.new_patient_btn)

    def click_patient(self, patient_name: str) -> None:
        """Click on a specific patient in the list."""
        patient_row = self.page.get_by_text(patient_name)
        self.click(patient_row)

    def logout(self) -> None:
        """Click logout button."""
        self.click(self.logout_btn)

    # ── Assertions ──────────────────────────────

    def verify_dashboard_loaded(self) -> None:
        """Assert dashboard page elements are visible."""
        self.expect_visible(self.page_title)
        self.expect_visible(self.nav_menu)

    def verify_patient_list_visible(self) -> None:
        """Assert patient list widget is displayed."""
        self.expect_visible(self.patient_list)

    def verify_stats_displayed(self) -> None:
        """Assert statistics widget is visible."""
        self.expect_visible(self.stats_widget)

    def verify_patient_in_list(self, patient_name: str) -> None:
        """Assert a patient appears in the patient list."""
        patient_entry = self.patient_list.get_by_text(patient_name)
        self.expect_visible(patient_entry)

    def verify_search_results(self, expected_count: int | None = None) -> None:
        """Assert search results are displayed."""
        if expected_count is not None:
            results = self.patient_list.locator("[data-testid='patient-row']")
            expect(results).to_have_count(expected_count)
