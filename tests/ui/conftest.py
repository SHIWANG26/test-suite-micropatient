"""
Playwright fixtures for UI tests.

Configures browser context, viewport, and provides page object
instances via dependency injection into tests.
"""

import pytest
from playwright.sync_api import Page

from config.settings import get_settings
from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.dashboard_page import DashboardPage
from tests.ui.pages.chat_page import ChatPage
from tests.ui.pages.patient_portal_page import PatientPortalPage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Override default Playwright browser context settings."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """Inject LoginPage page object."""
    return LoginPage(page)


@pytest.fixture
def dashboard_page(page: Page) -> DashboardPage:
    """Inject DashboardPage page object."""
    return DashboardPage(page)


@pytest.fixture
def chat_page(page: Page) -> ChatPage:
    """Inject ChatPage page object."""
    return ChatPage(page)


@pytest.fixture
def patient_portal_page(page: Page) -> PatientPortalPage:
    """Inject PatientPortalPage page object."""
    return PatientPortalPage(page)
