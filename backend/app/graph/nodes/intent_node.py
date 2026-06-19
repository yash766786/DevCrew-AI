from app.agents.intent_agent import intent_agent
from app.websocket.events import emit_event

def intent_node(state):
    emit_event(
        state["session_id"],
        "Intent Agent",
        "running",
        "Understanding user feedback..."
    )
    result = intent_agent(state["human_message"])
    emit_event(
        state["session_id"],
        "Intent Agent",
        "completed",
        f"Action detected: {result['action']}"
    )

    return {
        "action": result["action"]
    }