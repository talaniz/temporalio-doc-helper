from app.slack.handlers import handle_message, handle_reaction


async def handle_slack_event(payload):
    """Route Slack events by type."""
    print("Incoming payload:", payload)
    event = payload.get("event", {})
    if "bot_id" in event:
        return {"status": "ignored"}

    event_type = event.get("type")

    if event_type == "message":
        return await handle_message(event)
    elif event_type == "reaction_added":
        return await handle_reaction(event)
    else:
        return {"status": "unhandled"}
