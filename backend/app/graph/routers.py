# app/graph/routers.py
from langgraph.graph import END


def scope_router(state):
    if state["scope_allowed"]:
        return "planner"

    return END


def intent_router(state):
    if state["action"] == "approve":
        return END

    return "scope"


def modification_scope_router(state):
    if state["scope_allowed"]:
        return "plan_editor"

    return END


def build_router(state):
    if state["build_success"]:
        return "preview"

    if state["retry_count"] >= 3:
        return END

    return "reviewer"


def modify_intent_router(state):
    if state["action"] == "approve":
        return "satisfaction"

    return "scope"


def modify_scope_router(state):
    if state["scope_allowed"]:
        return "editor"

    return END

