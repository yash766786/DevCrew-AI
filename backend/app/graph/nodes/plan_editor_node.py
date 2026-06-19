from app.agents.plan_editor import plan_editor_agent
from app.websocket.events import emit_event

def plan_editor_node(state):
    emit_event(
        state["session_id"],
        "Plan Editor Agent",
        "running",
        "Updating project plan..."
    )
    updated_plan = plan_editor_agent(state["plan"], state["human_message"])
    emit_event(
        state["session_id"],
        "Plan Editor Agent",
        "completed",
        "Project plan updated"
    )

    return {
        "plan": updated_plan.model_dump(),
        "plan_summary": updated_plan.summary,
        "status": "awaiting_approval"
    }