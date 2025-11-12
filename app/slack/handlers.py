import asyncio
import os
from datetime import timedelta
from typing import Dict
from uuid import uuid4

from temporalio.client import Client
from temporalio.common import WorkflowIDReusePolicy

from app.slack.utils import send_message_to_slack

TEMPORAL_TASK_QUEUE = "qa-task-queue"
_temporal_client: Client | None = None
_client_lock = asyncio.Lock()


async def get_temporal_client() -> Client:
    global _temporal_client
    async with _client_lock:
        if _temporal_client is None:
            _temporal_client = await Client.connect("localhost:7233")
    return _temporal_client


async def _classify_with_workflow(text: str) -> dict:
    client: Client = await get_temporal_client()

    # Use a stable, positive id
    wf_id = f"classify-{abs(hash(text)) % 10_000_000}"
    return await client.execute_workflow(
        "ClassifyQuestionWorkflow",
        text,
        id=wf_id,
        task_queue=TEMPORAL_TASK_QUEUE,
        id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE,  # avoids collision
    )


async def handle_message(event: Dict) -> Dict:
    text = event.get("text", "")
    channel = event.get("channel")
    if not text or not channel:
        return None

    # 1) Classify via workflow
    try:
        cls = await _classify_with_workflow(text)
    except Exception as e:
        print(e)
        logger.exception("Classification workflow call failed")
        await send_message_to_slack(
            channel,
            "My classifier is having trouble right now—try again in a minute."
        )
        return None

    if not cls.get("ok"):
        # The workflow finished but the backend was unreachable after retries
        await send_message_to_slack(
            channel,
            "My docs brain is temporarily offline (LLM backend unavailable). I’ll be ready again shortly."
        )
        return None

    if not cls.get("is_temporal"):
        # Optional: stay silent or send a soft nudge
        # return None
        await send_message_to_slack(channel, "That one doesn’t look Temporal-related. Ask me about Temporal, or tag me with `temporal:`.")
        return None

    # 2) Proceed to the QA workflow as you already do
    await send_message_to_slack(channel, "Good question! Let me check the docs for you…")

    try:
        client: Client = await get_temporal_client()
        handle = await client.start_workflow(
            "AnswerTemporalQuestionWorkflow",
            text,
            id=f"qa-{abs(hash(text)) % 10_000_000}",
            task_queue=TEMPORAL_TASK_QUEUE,
        )
        answer = await handle.result()
        await send_message_to_slack(channel, answer)
    except Exception:
        logger.exception("QA workflow failed")
        await send_message_to_slack(
            channel,
            "I couldn’t reach the answer service just now. I’ll keep trying, but feel free to ask again in a bit."
        )

    return None

async def handle_reaction(event: Dict) -> Dict:
    reaction = event.get("reaction")
    item = event.get("item", {})
    user = event.get("user")

    print(f"User {user} reacted wtih :{reaction} to {item}")

    return {"status": "ok"}
