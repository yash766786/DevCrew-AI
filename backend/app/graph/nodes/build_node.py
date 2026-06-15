from app.services.docker_build import build_project_in_docker

def build_node(state):
    result = build_project_in_docker(state["project_id"])
    print(f"build node function (building in docker)-----------\n{result}")

    return {
        "build_success": result["success"],
        "build_output": result["build_output"],
        "build_error": result["build_error"]
    }