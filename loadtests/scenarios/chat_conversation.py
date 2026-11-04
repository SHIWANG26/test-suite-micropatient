"""
Chat Conversation Scenario — Simulates AI chat interactions under load.

Models patients sending messages and receiving AI responses.
This is the most latency-sensitive scenario — 50% of total traffic.
"""

import random

from locust import task, between

from loadtests.scenarios.api_stress import BaseAPIUser

SAMPLE_QUESTIONS = [
    "What are the common side effects of Metformin?",
    "How should I prepare for a colonoscopy?",
    "What symptoms should I watch for after a concussion?",
    "Can I take ibuprofen and acetaminophen together?",
    "How much water should I drink daily?",
    "What are the early warning signs of a stroke?",
    "What happens during an MRI scan?",
    "What should I know about taking antibiotics?",
    "How many hours of sleep do adults need?",
    "What vaccinations do adults need?",
]


class ChatConversationUser(BaseAPIUser):
    """
    Simulates patients chatting with the AI under load.

    Weighted at 50% of total load. This is the primary user path
    and the most performance-critical flow. Tracks latency closely.
    """

    weight = 5
    wait_time = between(3, 8)

    @task(10)
    def send_chat_message(self):
        """Send a medical question to the AI chat endpoint."""
        question = random.choice(SAMPLE_QUESTIONS)
        self.client.post(
            "/api/v1/chat/messages",
            json={
                "conversation_id": f"conv-load-{random.randint(1, 100):03d}",
                "message": question,
                "patient_id": "pat-load-001",
            },
            headers=self.auth_headers,
            name="/api/v1/chat/messages",
        )

    @task(3)
    def start_new_conversation(self):
        """Start a new conversation (creates context)."""
        self.client.post(
            "/api/v1/chat/conversations",
            json={"patient_id": "pat-load-001"},
            headers=self.auth_headers,
            name="/api/v1/chat/conversations [POST]",
        )

    @task(5)
    def multi_turn_chat(self):
        """Simulate a 3-turn conversation flow."""
        conv_id = f"conv-multi-{random.randint(1, 50):03d}"
        turns = random.sample(SAMPLE_QUESTIONS, min(3, len(SAMPLE_QUESTIONS)))

        for turn in turns:
            self.client.post(
                "/api/v1/chat/messages",
                json={
                    "conversation_id": conv_id,
                    "message": turn,
                    "patient_id": "pat-load-001",
                },
                headers=self.auth_headers,
                name="/api/v1/chat/messages [multi-turn]",
            )

    @task(2)
    def view_conversation_history(self):
        """Fetch conversation history during chat."""
        self.client.get(
            f"/api/v1/chat/conversations/conv-load-{random.randint(1, 100):03d}",
            headers=self.auth_headers,
            name="/api/v1/chat/conversations/:id",
        )
