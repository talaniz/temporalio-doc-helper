import asyncio
from typing import Dict

from temporalio.client import Client

from app.slack.utils import send_message_to_slack
from app.llm.langchain_agent import is_temporal_question

_temporal_client: Client | None = None
_client_lock = asyncio.Lock()

async def get_temporal_client() -> Client:
    global _temporal_client
    async with _client_lock:
        if _temporal_client is None:
            _temporal_client = await Client.connect("localhost:7233")
    return _temporal_client

async def handle_message(event: Dict) -> Dict:
    text = event.get("text", "")
    channel = event["channel"]

    if not text:
        return

    if await is_temporal_question(text):
        await send_message_to_slack(channel, "Good question! Let me check the docs for you...")

        client = await get_temporal_client()
        handle = await client.start_workflow(
            "AnswerTemporalQuestionWorkflow",
            text,
            id=f"qa-{hash(text)}",
            task_queue="qa-task-queue"
        )

        answer = await handle.result()
        await send_message_to_slack(channel, answer)
    else:
        print(f"Ignored non-Temporal question: {text}")

async def handle_reaction(event: Dict) -> Dict:
    reaction = event.get("reaction")
    item = event.get("item", {})
    user = event.get("user")

    print(f"User {user} reacted wtih :{reaction} to {item}")

    return {"status": "ok"}