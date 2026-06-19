# app/graph/nodes/scope_node.py
from app.agents.scope_agent import scope_agent
from app.websocket.events import emit_event

def scope_node(state):
    emit_event(
        state["session_id"],
        "Scope Agent",
        "running",
        "Checking project scope..."
    )

    text = (
        state["human_message"]
        if state.get("human_message")
        else state["prompt"]
    )

    result = scope_agent(text)

    emit_event(
        state["session_id"],
        "Scope Agent",
        "completed",
        result["reason"]
    )

    return {
        "scope_allowed": result["allowed"],
        "scope_reason": result["reason"]
    }




# def scope_node(state):
#     result = scope_agent(state["prompt"])

#     return {
#         "scope_allowed": result["allowed"],
#         "scope_reason": result["reason"]
#     }