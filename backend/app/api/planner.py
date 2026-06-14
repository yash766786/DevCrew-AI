import uuid
from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.models.planner import PlannerRequest
from app.models.project import Project

from app.tools.file_tools import read_file, write_file, list_files

from app.services.project_store import projects
from app.services.workspace import create_workspace, get_workspace
from app.services.scaffold import scaffold_project
from app.services.docker_build import build_project_in_docker
from app.services.docker_preview import start_preview, stop_preview


from app.agents.editor import editor_agent

from app.services.zip_service import create_project_zip

# app/models/human_response.py
from pydantic import BaseModel

class HumanResponseRequest(BaseModel):
    message: str

router = APIRouter()




from app.graph.planning_graph import planning_graph
from app.graph.respond_graph import respond_graph
from app.graph.execution_graph import execution_graph


@router.post("/projects")
def create_project(request: PlannerRequest):
    result = planning_graph.invoke(
        {
            "prompt": request.prompt,
            "status": "created"
        }
    )
    print(result)
    if not result["scope_allowed"]:
        return {
            "status": "rejected",
            "reason": result["scope_reason"]
        }

    project_id = str(uuid.uuid4())

    projects[project_id] = {
        **result,
        "project_id": project_id
    }

    return {
        "project_id": project_id,
        "status": "awaiting_approval",
        "plan": result["plan"],
        "summary": result["plan_summary"]
    }



@router.post("/projects/{project_id}/respond")
def respond_to_plan(project_id: str, request: HumanResponseRequest):
    project = projects.get(project_id)
    if not project:
        return {
            "error": "Project not found"
        }

    result = respond_graph.invoke({
        **project,
        "human_message": request.message
    })

    # ---------- APPROVED ----------
    if result.get("action") == "approve":
        project.update(result)

        project["approved"] = True
        project["status"] = "approved"

        result = execution_graph.invoke({
            **project
        })

        return {
            "project_id": project_id,
            "status": result["status"],
            "preview_url": result["preview_url"]
        }

    # ---------- MODIFICATION REJECTED ----------
    if not result.get("scope_allowed", True):
        return {
            "project_id": project_id,
            "status": "rejected",
            "reason": result["scope_reason"]
        }

    # ---------- PLAN UPDATED ----------
    project.update(result)

    return {
        "project_id": project_id,
        "status": "awaiting_approval",
        "plan": result["plan"],
        "summary": result["plan_summary"]
    }



@router.post("/planner")
def generate_plan(request: PlannerRequest):

    # result = planner_graph.invoke(
    #     {
    #         "prompt": request.prompt
    #     }
    # )

    result = planning_graph.invoke(
        {
        "prompt": request.prompt
        }
    )

    print(result)

    project_id = str(uuid.uuid4())

    project = Project(
        project_id=project_id,
        prompt=request.prompt,
        plan=result["plan"],
        status="pending_approval"
    )

    projects[project_id] = project

    return {
        "project_id": project_id,
        "status": "pending_approval",
        "plan": result["plan"]
    }



@router.get("/projects/{project_id}")
def get_project(project_id: str):

    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    return project



@router.post("/projects/{project_id}/approve")
def approve_project(project_id: str):

    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    project.status = "approved"

    return {
        "project_id": project_id,
        "status": project.status
    }



# @router.post("/projects/{project_id}/modify")
# def modify_project(
#     project_id: str,
#     request: ModifyRequest
# ):

#     project = projects.get(project_id)

#     if not project:
#         return {
#             "error": "Project not found"
#         }

#     return {
#         "message": "Modification workflow coming soon",
#         "feedback": request.feedback
#     }



@router.post("/projects/{project_id}/generate")
def generate_project(project_id: str):

    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    if project.status != "approved":
        return {
            "error": "Project must be approved first"
        }

    create_workspace(project_id)

    scaffold_project(project_id)

    developer_agent(
        project_id=project_id,
        plan=project.plan
    )

    project.status = "generated"

    return {
        "project_id": project_id,
        "status": "generated"
    }



@router.get("/projects/{project_id}/files")
def get_project_files(project_id: str):

    return {
        "files": list_files(project_id)
    }



@router.get("/projects/{project_id}/page")
def get_page(project_id: str):

    content = read_file(
        project_id,
        "app/page.tsx"
    )

    return {
        "content": content
    }



# @router.post("/projects/{project_id}/build")
# def build_generated_project(project_id: str):

#     project = projects.get(project_id)

#     if not project:
#         return {
#             "error": "Project not found"
#         }

#     workspace = get_workspace(project_id)

#     result = build_project(workspace)

#     project.status = (
#         "build_success"
#         if result["success"]
#         else "build_failed"
#     )

#     return {
#         "project_id": project_id,
#         "status": project.status,
#         "success": result["success"],
#         "logs": result["build_output"],
#         "errors": result["build_error"]
#     }


@router.get("/projects/{project_id}/page")
def get_page(project_id: str):

    content = read_file(
        project_id,
        "app/page.tsx"
    )

    return {
        "content": content
    }


from app.services.build_workflow import build_with_retry

@router.post("/projects/{project_id}/build")
def build_generated_project(project_id: str):

    project = projects.get(project_id)

    workspace = get_workspace(project_id)

    response = build_with_retry(
        project_id,
        workspace
    )

    project.status = (
        "build_success"
        if response["success"]
        else "build_failed"
    )

    return response


@router.post("/projects/{project_id}/preview")
def preview_project(project_id: str):

    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    workspace = get_workspace(project_id)

    session = start_preview(
        project_id,
        workspace
    )

    return {
        "project_id": project_id,
        "preview_url": f"http://localhost:{session['port']}"
    }


@router.post("/projects/{project_id}/stop-preview")
def stop_project_preview(project_id: str):

    success = stop_preview(project_id)

    return {
        "success": success
    }


@router.post("/projects/{project_id}/modify")
def modify_project(project_id: str, request: ModifyRequest):

    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    current_code = read_file(
        project_id,
        "app/page.tsx"
    )

    updated_code = editor_agent(
        current_code=current_code,
        user_request=request.message
    )

    write_file(
        project_id,
        "app/page.tsx",
        updated_code
    )

    return {
        "status": "modified"
    }


@router.get("/projects/{project_id}/download")
def download_project(project_id: str):

    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    workspace = get_workspace(
        project_id
    )

    zip_path = (
        workspace.parent /
        f"{project_id}.zip"
    )

    create_project_zip(
        workspace,
        zip_path
    )

    return FileResponse(
        path=zip_path,
        filename=f"{project_id}.zip",
        media_type="application/zip"
    )


@router.post("/projects/{project_id}/docker-build")
def docker_build_project(project_id: str):

    workspace = get_workspace(project_id)
    result = build_project_in_docker(workspace)

    return result


@router.post("/projects/{project_id}/docker-preview")
def preview_project(project_id: str):

    project = projects.get(project_id)

    if not project:
        return {
            "error": "Project not found"
        }

    workspace = get_workspace(project_id)

    session = start_preview(
        project_id,
        workspace
    )

    return {
        "project_id": project_id,
        "preview_url": f"http://localhost:{session['port']}"
    }


@router.post("/projects/{project_id}/docker-stop-preview")
def stop_project_preview(project_id: str):

    success = stop_preview(project_id)

    return {
        "success": success
    }


