"""
BasePage — Abstract base class for all Page Objects.

Encapsulates common Playwright interactions: navigation, clicking,
typing, waiting, and screenshot capture. All page objects inherit
from this class to avoid code duplication.
"""

from __future__ import annotations

import logging
from typing import Any

from playwright.sync_api import Page, expect, Locator

logger = logging.getLogger(__name__)


class BasePage:
    """Base page object with shared Playwright interaction methods."""

    def __init__(self, page: Page):
        self.page = page

    # ── Navigation ──────────────────────────────

    def navigate(self, url: str) -> None:
        """Navigate to a URL and wait for load."""
        logger.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded")

    def get_current_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    def reload(self) -> None:
        """Reload the current page."""
        self.page.reload(wait_until="domcontentloaded")

    # ── Interactions ────────────────────────────

    def click(self, locator: Locator) -> None:
        """Click an element with auto-wait."""
        locator.click()

    def fill(self, locator: Locator, text: str) -> None:
        """Clear and fill an input field."""
        locator.fill(text)

    def type_text(self, locator: Locator, text: str, delay: int = 50) -> None:
        """Type text character by character with delay (simulates real typing)."""
        locator.type(text, delay=delay)

    def select_option(self, locator: Locator, value: str) -> None:
        """Select dropdown option by value."""
        locator.select_option(value)

    def get_text(self, locator: Locator) -> str:
        """Get visible text content of an element."""
        return locator.text_content() or ""

    def get_input_value(self, locator: Locator) -> str:
        """Get value of an input field."""
        return locator.input_value()

    # ── Waits & Assertions ──────────────────────

    def wait_for_element(self, selector: str, timeout: int = 10000) -> Locator:
        """Wait for element to be visible and return its locator."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator

    def wait_for_url(self, url_pattern: str, timeout: int = 10000) -> None:
        """Wait for URL to match the pattern."""
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def expect_visible(self, locator: Locator) -> None:
        """Assert element is visible."""
        expect(locator).to_be_visible()

    def expect_hidden(self, locator: Locator) -> None:
        """Assert element is hidden."""
        expect(locator).to_be_hidden()

    def expect_text(self, locator: Locator, text: str) -> None:
        """Assert element contains expected text."""
        expect(locator).to_contain_text(text)

    def expect_url_contains(self, substring: str) -> None:
        """Assert current URL contains substring."""
        expect(self.page).to_have_url(f"*{substring}*")

    # ── Utilities ───────────────────────────────

    def take_screenshot(self, name: str) -> bytes:
        """Capture a screenshot and return bytes."""
        return self.page.screenshot(path=f"reports/{name}.png", full_page=True)

    def get_page_title(self) -> str:
        """Return the page title."""
        return self.page.title()

    def is_element_visible(self, selector: str) -> bool:
        """Check if element is visible without waiting."""
        return self.page.locator(selector).is_visible()
