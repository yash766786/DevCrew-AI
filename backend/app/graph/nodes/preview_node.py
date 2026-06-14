from app.services.docker_preview import start_preview

def preview_node(state):
    result = start_preview(state["project_id"])

    return {
        "preview_url": result["preview_url"],
        "status": "preview_ready"
    }