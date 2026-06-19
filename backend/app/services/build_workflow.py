from app.services.build_service import build_project
from app.services.fix_loop import fix_project
from app.services.docker_build import (
    build_project_in_docker
)


def build_with_retry(
    project_id: str,
    workspace,
    max_attempts: int = 3
):

    attempt = 0

    while attempt < max_attempts:
        result = build_project_in_docker(workspace)

        if result["success"]:
            return {
                "success": True,
                "attempts": attempt + 1,
                "result": result
            }

        fix_project(
            project_id,
            result["build_error"]
        )

        attempt += 1

    return {
        "success": False,
        "attempts": max_attempts,
        "result": result
    }