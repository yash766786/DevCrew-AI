# app/graph/nodes/scope_node.py


# def scope_node(state):
#     result = scope_agent(state["prompt"])

#     return {
#         "scope_allowed": result["allowed"],
#         "scope_reason": result["reason"]
#     }

from app.agents.scope_agent import scope_agent

def scope_node(state):
    text = (
        state["human_message"]
        if state.get("human_message")
        else state["prompt"]
    )

    result = scope_agent(text)

    return {
        "scope_allowed": result["allowed"],
        "scope_reason": result["reason"]
    }