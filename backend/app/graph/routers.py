# app/graph/routers.py
from langgraph.graph import END
from app.agents.planner import planner_agent


def scope_router(state):

    if state["scope_allowed"]:
        return "planner"

    return END


# def planner_node(state):

#     plan = planner_agent(
#         state["prompt"]
#     )

#     return {
#         "plan": plan.model_dump(),

#         "plan_summary": (
#             f"Project: {plan.project_name}\n"
#             f"Theme: {plan.theme}\n"
#             f"Sections: {', '.join(plan.sections)}"
#         )
#     }


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

