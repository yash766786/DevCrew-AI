# app/graph/nodes/editor_node.py
from app.agents.editor import editor_agent
from app.tools.file_tools import read_file, write_file
from app.websocket.events import emit_event


def editor_node(state):
    emit_event(
        state["session_id"],
        "Editor Agent",
        "running",
        "Applying requested changes..."
    )

    current_code = read_file(state["project_id"], "app/page.tsx")
    updated_code = editor_agent(current_code=current_code, user_request=state["human_message"])
    write_file(state["project_id"], "app/page.tsx", updated_code)
    
    emit_event(
        state["session_id"],
        "Editor Agent",
        "completed",
        "Website updated successfully"
    )

    return {
        "generated": True
    }