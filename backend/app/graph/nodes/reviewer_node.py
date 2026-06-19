from app.tools.file_tools import read_file
from app.agents.reviewer import reviewer_agent
from app.websocket.events import emit_event

def reviewer_node(state):
    emit_event(
        state["session_id"],
        "Reviewer Agent",
        "running",
        "Analyzing build failure..."
    )

    code = read_file(state["project_id"], "app/page.tsx")
    instructions = reviewer_agent(code, state["build_error"])
    emit_event(
        state["session_id"],
        "Reviewer Agent",
        "completed",
        "Fix instructions generated"
    )

    return {
        "fix_instructions": instructions
    }