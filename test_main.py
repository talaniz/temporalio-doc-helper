"""Testing module."""
import unittest

from fastapi.testclient import TestClient
from main import app

class TestSlackClient(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)


    def test_slack_challenge(self):
        """Test Slack challenge verification."""
        response = self.client.post("/slack/events", json={"challenge": "test_challenge"})
        assert response.status_code == 200
        assert response.json() == {"challenge": "test_challenge"}


    def test_slack_message(self):
        """Test Slack bot responding to a message."""
        event_data = {
            "event": {
                "text": "Hello, bot!",
                "channel": "C123456",
                "type": "message",
            }
        }
        response = self.client.post("/slack/events", json=event_data)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_slack_reaction(self):
        """Test Slack bot handling a reaction_added event."""
        event_data = {
            "event": {
                "type": "reaction_added",
                "reaction": "thumbsup",
                "item": {
                    "type": "message",
                    "channel": "C123456",
                    "ts": "1234567890.123456"
                },
                "user": "U123456"
            }
        }
        response = self.client.post("/slack/events", json=event_data)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
