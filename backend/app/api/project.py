import uuid
from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.models.planner import PlannerRequest, HumanFeedback
from app.services.project_store import projects
from app.graph.planning_graph import planning_graph
from app.graph.respond_graph import respond_graph
from app.graph.execution_graph import execution_graph
from app.graph.modify_graph import modify_graph
from app.services.zip_service import create_project_zip
from app.services.workspace import get_workspace

router = APIRouter()

@router.post("/projects")
def create_project(request: PlannerRequest):
    print("REQUEST:", request.model_dump())

    result = planning_graph.invoke(
        {
            "prompt": request.prompt,
            "status": "created",
            "session_id": request.session_id
        }
    )
    
    if not result["scope_allowed"]:
        return {
            "status": "rejected",
            "reason": result["scope_reason"]
        }
    

    project_id = str(uuid.uuid4())
    state = {
        **result,
        "project_id": project_id,
        "session_id": request.session_id
    }

    projects[project_id] = state
    print(f"\nprojects:----\n{projects}")
    

    return {
        "project_id": project_id,
        "status": "awaiting_approval",
        "plan": result["plan"],
        "summary": result["plan_summary"]
    }


# @router.post("/projects/{project_id}/respond")
# def respond_to_plan(project_id: str, request: HumanFeedback):
#     # ---------------- LOAD STATE ----------------
#     project = projects.get(project_id)
#     if not project:
#         return {
#             "error": "Project not found"
#         }

#     # ---------------- HUMAN FEEDBACK GRAPH ----------------
#     result = respond_graph.invoke({
#         **project,
#         "human_message": request.message
#     })

#     # ---------------- APPROVED ----------------
#     if result.get("action") == "approve":
#         project.update(result)
#         project["approved"] = True
#         project["status"] = "approved"

#         execution_result = execution_graph.invoke({
#             **project,
#             "generated": False,
#             "build_success": False,
#             "build_output": "",
#             "build_error": "",
#             "fix_instructions": "",
#             "retry_count": 0,
#             "preview_url": ""
#         })

#         project.update(execution_result)
#         print(f"\nprojects2:----\n{projects}")

#         return {
#             "project_id": project_id,
#             "status": execution_result["status"],
#             "preview_url": execution_result["preview_url"]
#         }

#     # ---------------- MODIFICATION REJECTED ----------------

#     if not result.get("scope_allowed", True):
#         print(f"\nprojects:----\n{projects}")
#         return {
#             "project_id": project_id,
#             "status": "rejected",
#             "reason": result["scope_reason"]
#         }

#     # ---------------- PLAN UPDATED ----------------
#     project.update(result)
#     print(f"\nprojects:----\n{projects}")
#     # return {
#     #     "project_id": project_id,
#     #     "status": "awaiting_approval",
#     #     "plan": result["plan"],
#     #     "summary": result["plan_summary"]
#     # }
#     return {
#     "project_id": project_id,
#     "status": execution_result["status"],
#     "preview_url": execution_result["preview_url"],
#     "build_success": execution_result.get("build_success", False),
#     "retry_count": execution_result.get("retry_count", 0),
#     "build_error": (execution_result.get("build_error") or "")[-500:],
# }

@router.post("/projects/{project_id}/respond")
def respond_to_plan(project_id: str, request: HumanFeedback):
    # ---------------- LOAD STATE ----------------
    project = projects.get(project_id)
    if not project:
        return {
            "error": "Project not found"
        }

    # ---------------- HUMAN FEEDBACK GRAPH ----------------
    result = respond_graph.invoke({
        **project,
        "human_message": request.message
    })

    # ---------------- APPROVED ----------------
    if result.get("action") == "approve":
        project.update(result)
        project["approved"] = True
        project["status"] = "approved"

        execution_result = execution_graph.invoke({
            **project,
            "generated": False,
            "build_success": False,
            "build_output": "",
            "build_error": "",
            "fix_instructions": "",
            "retry_count": 0,
            "preview_url": ""
        })

        project.update(execution_result)
        print(f"\nprojects2:----\n{projects}")

        return {
            "project_id": project_id,
            "status": execution_result["status"],
            "preview_url": execution_result["preview_url"],
            "build_success": execution_result.get("build_success", False),
            "retry_count": execution_result.get("retry_count", 0),
            "build_error": (execution_result.get("build_error") or "")[-500:],
        }

    # ---------------- MODIFICATION REJECTED ----------------

    if not result.get("scope_allowed", True):
        print(f"\nprojects:----\n{projects}")
        return {
            "project_id": project_id,
            "status": "rejected",
            "reason": result["scope_reason"]
        }

    # ---------------- PLAN UPDATED ----------------
    project.update(result)
    print(f"\nprojects:----\n{projects}")
    return {
        "project_id": project_id,
        "status": "awaiting_approval",
        "plan": result["plan"],
        "summary": result["plan_summary"]
    }

@router.post("/projects/{project_id}/modify")
def modify_project(project_id: str, request: HumanFeedback):
    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    result = modify_graph.invoke({
        **project,
        "human_message": request.message
    })
    project.update(result)
    print(f"\nprojects3:----\n{projects}")

    # USER SATISFIED
    if result.get("action") == "approve":
        return {
            "project_id": project_id,
            "status": "preview_ready",
            "message": result["assistant_response"]
        }

    # MODIFICATION REJECTED
    if not result.get("scope_allowed", True):
        return {
            "project_id": project_id,
            "status": "rejected",
            "reason": result["scope_reason"]
        }

    # MODIFICATION APPLIED
    return {
        "project_id": project_id,
        "status": result["status"],
        "preview_url": result["preview_url"]
    }


@router.get("/projects/{project_id}/download")
def download_project(project_id: str):

    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    workspace = get_workspace(project_id)

    zip_path = (
        workspace.parent /
        f"{project_id}.zip"
    )

    create_project_zip(workspace, zip_path)

    return FileResponse(
        path=zip_path,
        filename=f"{project_id}.zip",
        media_type="application/zip"
    )

