# app/graph/nodes/satisfaction_node.py
from app.agents.satisfaction_agent import satisfaction_agent
from app.websocket.events import emit_event

def satisfaction_node(state):
    emit_event(
        state["session_id"],
        "Satisfaction Agent",
        "running",
        "Generating response..."
    )

    response = satisfaction_agent(state["human_message"])

    emit_event(
        state["session_id"],
        "Satisfaction Agent",
        "completed",
        "User is satisfied with the result"
    )

    return {
        "assistant_response": response,
        "status": "completed"
    }