# # # from typing import TypedDict


# # # class PlanningState(TypedDict):
# # #     prompt: str

# # #     scope_allowed: bool
# # #     scope_reason: str

# # #     plan: dict
# # #     plan_summary: str

# # #     human_response: str

# # #     action: str

# # #     approved: bool

# # # app/graph/state.py

# # from typing import TypedDict, Optional


# # class ProjectState(TypedDict):
# #     # ---------- USER ----------
# #     project_id: str
# #     prompt: str

# #     # ---------- SCOPE ----------
# #     scope_allowed: bool
# #     scope_reason: str

# #     # ---------- PLANNING ----------
# #     plan: dict
# #     plan_summary: str

# #     # ---------- HUMAN LOOP ----------
# #     human_message: str
# #     action: str
# #     approved: bool

# #     # ---------- GENERATION ----------
# #     generated_code: str

# #     # ---------- BUILD ----------
# #     build_success: bool
# #     build_output: str
# #     build_error: str

# #     # ---------- REVIEW ----------
# #     fix_instructions: str

# #     # ---------- RETRY ----------
# #     retry_count: int

# #     # ---------- PREVIEW ----------
# #     preview_url: str

# #     # ---------- DEPLOY ----------
# #     deployment_url: str

# #     # ---------- EVENTS ----------
# #     events: list[str]


# # app/graph/state.py

# from typing import TypedDict
# class ProjectState(TypedDict):

#     # user
#     project_id: str
#     prompt: str

#     # scope
#     scope_allowed: bool
#     scope_reason: str

#     # planning
#     plan: dict
#     plan_summary: str

#     # human
#     human_message: str
#     action: str
#     approved: bool

#     # status
#     status: str


from typing import TypedDict


class ProjectState(TypedDict):
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

    