from typing import Dict

from app.slack.utils import send_message_to_slack

async def handle_message(event: Dict) -> Dict:
    text = event.get("text", "").lower()
    channel = event.get("channel")

    print("handle_message triggered:", event)

    if "hello" in text:
        await send_message_to_slack(channel, "Hello, world! :wave:")
    return {"status": "ok"}

async def handle_reaction(event: Dict) -> Dict:
    reaction = event.get("reaction")
    item = event.get("item", {})
    user = event.get("user")

    print(f"User {user} reacted wtih :{reaction} to {item}")

    return {"status": "ok"}