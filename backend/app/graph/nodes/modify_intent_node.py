# app/graph/nodes/modify_intent_node.py
from app.agents.intent_agent import intent_agent
from app.websocket.events import emit_event

def modify_intent_node(state):
    emit_event(
        state["session_id"],
        "Modify Intent Agent",
        "running",
        "Understanding modification request..."
    )
    result = intent_agent(state["human_message"])

    emit_event(
        state["session_id"],
        "Modify Intent Agent",
        "completed",
        f"Action detected: {result['action']}"
    )

    return {
        "action": result["action"]
    }
