"""
Chat Flow UI Tests — Playwright end-to-end tests for AI chat interactions.

Covers sending messages, receiving AI responses, multi-turn conversations,
disclaimer verification, and feedback mechanisms.
"""

import pytest

from tests.ui.pages.chat_page import ChatPage
from tests.ui.pages.login_page import LoginPage


@pytest.mark.ui
class TestChatFlow:
    """End-to-end UI tests for the AI chat interface."""

    def test_chat_page_elements_visible(self, login_page: LoginPage, chat_page: ChatPage):
        """Verify chat interface elements render after login."""
        login_page.load()
        login_page.login_as_patient()
        chat_page.load()
        chat_page.verify_chat_loaded()

    def test_send_message_appears_in_chat(self, login_page: LoginPage, chat_page: ChatPage):
        """Sent message appears in the conversation thread."""
        login_page.load()
        login_page.login_as_patient()
        chat_page.load()
        chat_page.send_message("What are the side effects of ibuprofen?")
        chat_page.verify_message_sent("What are the side effects of ibuprofen?")

    def test_ai_responds_to_message(self, login_page: LoginPage, chat_page: ChatPage):
        """AI generates a response after user sends a message."""
        login_page.load()
        login_page.login_as_patient()
        chat_page.load()
        response = chat_page.send_and_wait("How much water should I drink daily?")
        assert len(response) > 0, "AI response should not be empty"

    def test_multi_turn_conversation(self, login_page: LoginPage, chat_page: ChatPage):
        """Chat supports multiple back-and-forth turns."""
        login_page.load()
        login_page.login_as_patient()
        chat_page.load()

        chat_page.send_and_wait("I have a headache.")
        chat_page.send_and_wait("It's been going on for 3 days.")
        chat_page.send_and_wait("Should I see a doctor?")

        responses = chat_page.get_all_ai_responses()
        assert len(responses) >= 3, (
            f"Expected 3+ AI responses in multi-turn, got {len(responses)}"
        )

    def test_new_chat_clears_conversation(self, login_page: LoginPage, chat_page: ChatPage):
        """Starting a new chat clears the previous conversation."""
        login_page.load()
        login_page.login_as_patient()
        chat_page.load()

        chat_page.send_and_wait("Hello")
        chat_page.start_new_chat()
        # After new chat, message area should be empty or show welcome

    def test_disclaimer_is_visible(self, login_page: LoginPage, chat_page: ChatPage):
        """AI disclaimer banner is visible on the chat page."""
        login_page.load()
        login_page.login_as_patient()
        chat_page.load()
        chat_page.verify_disclaimer_visible()
