from typing import TypedDict

class ProjectState(TypedDict):
    # SESSION
    session_id: str

    # PROJECT
    project_id: str
    prompt: str

    # SCOPE
    scope_allowed: bool
    scope_reason: str

    # PLANNING
    plan: dict
    plan_summary: str

    # HUMAN LOOP
    human_message: str
    action: str
    approved: bool

    # GENERATION
    generated: bool

    # BUILD
    build_success: bool
    build_output: str
    build_error: str

    # REVIEW / FIX
    fix_instructions: str
    retry_count: int

    # PREVIEW
    preview_url: str

    # STATUS
    status: str

    assistant_response: str

    