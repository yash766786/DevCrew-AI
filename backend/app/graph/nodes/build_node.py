from app.services.docker_build import build_project_in_docker
from app.websocket.events import emit_event

def build_node(state):
    emit_event(
        state["session_id"],
        "Build Agent",
        "running",
        "Building Next.js application..."
    )

    result = build_project_in_docker(state["project_id"])
    print(f"build node function (building in docker)-----------\n{result}")
    
    if result["success"]:
        emit_event(
            state["session_id"],
            "Build Agent",
            "completed",
            "Build completed successfully"
        )
    else:
        emit_event(
        state["session_id"],
            "Build Agent",
            "failed",
            "Build failed.."
        )

    return {
        "build_success": result["success"],
        "build_output": result["build_output"],
        "build_error": result["build_error"]
    }