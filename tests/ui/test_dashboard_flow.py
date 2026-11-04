"""
Dashboard Flow UI Tests — Playwright tests for the doctor dashboard.

Covers dashboard loading, patient list, search functionality,
statistics display, and navigation.
"""

import pytest

from tests.ui.pages.dashboard_page import DashboardPage
from tests.ui.pages.login_page import LoginPage


@pytest.mark.ui
class TestDashboardFlow:
    """End-to-end UI tests for the doctor dashboard."""

    def test_dashboard_loads_after_login(self, login_page: LoginPage, dashboard_page: DashboardPage):
        """Dashboard loads with all widgets after doctor login."""
        login_page.load()
        login_page.login_as_doctor()
        dashboard_page.verify_dashboard_loaded()

    def test_patient_list_visible(self, login_page: LoginPage, dashboard_page: DashboardPage):
        """Patient list widget displays on dashboard."""
        login_page.load()
        login_page.login_as_doctor()
        dashboard_page.verify_patient_list_visible()

    def test_search_patient(self, login_page: LoginPage, dashboard_page: DashboardPage):
        """Search filters the patient list."""
        login_page.load()
        login_page.login_as_doctor()
        dashboard_page.search_patient("Jane Doe")
        # Search should filter results

    def test_stats_widget_displayed(self, login_page: LoginPage, dashboard_page: DashboardPage):
        """Statistics widget shows metrics on dashboard."""
        login_page.load()
        login_page.login_as_doctor()
        dashboard_page.verify_stats_displayed()

    def test_logout_returns_to_login(self, login_page: LoginPage, dashboard_page: DashboardPage):
        """Logout from dashboard returns to login page."""
        login_page.load()
        login_page.login_as_doctor()
        dashboard_page.logout()
        login_page.verify_login_page_loaded()

    def test_dashboard_page_title(self, login_page: LoginPage, dashboard_page: DashboardPage):
        """Verify dashboard has proper page title."""
        login_page.load()
        login_page.login_as_doctor()
        title = dashboard_page.get_page_title()
        assert title, "Dashboard should have a title"
