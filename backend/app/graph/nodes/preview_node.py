from app.services.docker_preview import start_preview, restart_preview, preview_sessions
from app.websocket.events import emit_event

def preview_node(state):
    emit_event(
        state["session_id"],
        "Preview Agent",
        "running",
        "Launching preview server..."
    )
    project_id = state["project_id"]
    
    # result = start_preview(state["project_id"])
    if project_id in preview_sessions:
        result = restart_preview(project_id)
    else:
        result = start_preview(project_id)

    emit_event(
        state["session_id"],
        "Preview Agent",
        "completed",
        "Launched the server"
    )

    emit_event(
        state["session_id"],
        "preview_ready",
        "completed",
        result["preview_url"]
    )

    return {
        "preview_url": result["preview_url"],
        "status": "preview_ready"
    }