"""
ChatPage — Page Object for the AI Chat interface.

Encapsulates chat message input, conversation display, typing
indicators, and AI response validation for the chat window.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import get_settings
from tests.ui.pages.base_page import BasePage


class ChatPage(BasePage):
    """Page object for the Micropatient AI Chat interface."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.settings = get_settings()

        # ── Locators ────────────────────────────
        self.message_input = page.get_by_placeholder("Type your message")
        self.send_button = page.get_by_role("button", name="Send")
        self.chat_container = page.locator("[data-testid='chat-messages']")
        self.typing_indicator = page.locator("[data-testid='typing-indicator']")
        self.user_messages = page.locator("[data-testid='user-message']")
        self.ai_messages = page.locator("[data-testid='ai-message']")
        self.new_chat_btn = page.get_by_role("button", name="New Chat")
        self.chat_history_sidebar = page.locator("[data-testid='chat-history']")
        self.disclaimer_banner = page.locator("[data-testid='ai-disclaimer']")
        self.feedback_thumbs_up = page.locator("[data-testid='feedback-up']")
        self.feedback_thumbs_down = page.locator("[data-testid='feedback-down']")

    # ── Actions ─────────────────────────────────

    def load(self) -> None:
        """Navigate to the chat interface."""
        self.navigate(f"{self.settings.MICROPATIENT_UI_URL}/chat")

    def send_message(self, message: str) -> None:
        """Type and send a message to the AI."""
        self.fill(self.message_input, message)
        self.click(self.send_button)

    def wait_for_ai_response(self, timeout: int = 30000) -> str:
        """Wait for AI response to appear and return its text."""
        # Wait for typing indicator to disappear
        self.page.wait_for_timeout(500)
        last_ai_message = self.ai_messages.last
        last_ai_message.wait_for(state="visible", timeout=timeout)
        return self.get_text(last_ai_message)

    def send_and_wait(self, message: str, timeout: int = 30000) -> str:
        """Send a message and wait for the AI response."""
        current_count = self.ai_messages.count()
        self.send_message(message)
        # Wait for a new AI message to appear
        self.page.wait_for_function(
            f"document.querySelectorAll('[data-testid=\"ai-message\"]').length > {current_count}",
            timeout=timeout,
        )
        return self.get_text(self.ai_messages.last)

    def start_new_chat(self) -> None:
        """Start a new conversation."""
        self.click(self.new_chat_btn)

    def give_feedback(self, positive: bool = True) -> None:
        """Click thumbs up or thumbs down on the last AI response."""
        if positive:
            self.click(self.feedback_thumbs_up.last)
        else:
            self.click(self.feedback_thumbs_down.last)

    # ── Assertions ──────────────────────────────

    def verify_chat_loaded(self) -> None:
        """Assert chat interface elements are visible."""
        self.expect_visible(self.message_input)
        self.expect_visible(self.send_button)

    def verify_disclaimer_visible(self) -> None:
        """Assert AI disclaimer banner is displayed."""
        self.expect_visible(self.disclaimer_banner)

    def verify_message_sent(self, message: str) -> None:
        """Assert the user's message appears in the chat."""
        last_user_msg = self.user_messages.last
        self.expect_text(last_user_msg, message)

    def verify_ai_responded(self) -> None:
        """Assert at least one AI message is visible."""
        expect(self.ai_messages).to_have_count(1)

    def verify_message_count(self, user_count: int, ai_count: int) -> None:
        """Assert specific number of user and AI messages."""
        expect(self.user_messages).to_have_count(user_count)
        expect(self.ai_messages).to_have_count(ai_count)

    def get_all_ai_responses(self) -> list[str]:
        """Return text of all AI response messages."""
        count = self.ai_messages.count()
        return [self.get_text(self.ai_messages.nth(i)) for i in range(count)]
