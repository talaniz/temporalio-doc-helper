import os

import httpx

SLACK_API_URL = "https://slack.com/api/chat.postMessage"


async def send_message_to_slack(channel: str, message: str):
    """Handle Slackbot responses."""
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    print("Sending message to Slack:")
    print("Channel:", channel)
    print("Message:", message)
    print("Token present:", bool(SLACK_BOT_TOKEN))

    async with httpx.AsyncClient() as client:
        response = await client.post(
            SLACK_API_URL,
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": message}
        )
    return response.json()
