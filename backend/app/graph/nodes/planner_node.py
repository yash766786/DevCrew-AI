# app/graph/nodes/planner_node.py
from app.agents.planner import planner_agent

def planner_node(state):
    plan = planner_agent(state["prompt"])

    return {
        "plan": plan.model_dump(),
        "plan_summary": plan.summary,
        "status": "awaiting_approval"
    }


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