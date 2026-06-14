from app.agents.plan_editor import plan_editor_agent


def plan_editor_node(state):
    updated_plan = plan_editor_agent(
        state["plan"],
        state["human_message"]
    )

    return {
        "plan": updated_plan.model_dump(),
        "plan_summary": updated_plan.summary,
        "status": "awaiting_approval"
    }