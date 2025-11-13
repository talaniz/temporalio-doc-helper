from typing import Dict

from app.slack.utils import send_message_to_slack
from app.llm.langchain_agent import is_temporal_question, answer_temporal_question


async def handle_message(event: Dict) -> Dict:
    """Route messages by message content."""
    text = event.get("text", "")
    channel = event["channel"]

    if not text:
        return

    if await is_temporal_question(text):
        await send_message_to_slack(channel, "Good question! Let me check the docs for you...")
        answer = await answer_temporal_question(text)
        await send_message_to_slack(channel, answer)
    else:
        print(f"Ignored non-Temporal question: {text}")


async def handle_reaction(event: Dict) -> Dict:
    """Handle input based on emoji reactions."""
    reaction = event.get("reaction")
    item = event.get("item", {})
    user = event.get("user")

    print(f"User {user} reacted wtih :{reaction} to {item}")

    return {"status": "ok"}
