# app/graph/nodes/planner_node.py
from app.agents.planner import planner_agent
from app.websocket.events import emit_event

def planner_node(state):
    emit_event(
    state["session_id"],
        "Planner Agent",
        "running",
        "Creating project plan..."
    )
    plan = planner_agent(state["prompt"])
    print(f"plan:-------------\n{plan}")
    emit_event(
        state["session_id"],
        "Planner Agent",
        "completed",
        f"Plan created for {plan.project_name}"
    )

    return {
        "plan": plan.model_dump(),
        "plan_summary": plan.summary,
        "status": "awaiting_approval"
    }

