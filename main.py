import asyncio
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from app.slack.router import handle_slack_event

load_dotenv()

SLACK_BOT_USER_ID = os.getenv("SLACK_BOT_USER_ID")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_API_URL = "https://slack.com/api/chat.postMessage"

app = FastAPI()


@app.post("/slack/events")
async def slack_events(request: Request):
    """Handles incoming Slack messages and responds if bot is mentioned."""
    payload = await request.json()

    if "challenge" in payload:
        return {"challenge": payload["challenge"]}

    asyncio.create_task(handle_slack_event(payload))
    return {"status": "ok"}
