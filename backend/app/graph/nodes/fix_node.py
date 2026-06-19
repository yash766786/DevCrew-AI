from app.tools.file_tools import read_file, write_file
from app.agents.developer_fix_agent import developer_fix_agent
from app.websocket.events import emit_event

def fix_node(state):
    emit_event(
    state["session_id"],
        "Code Fixer Agent",
        "running",
        "Applying automatic fixes..."
    )
    code = read_file(state["project_id"], "app/page.tsx")
    fixed_code = developer_fix_agent(code, state["fix_instructions"])
    write_file(state["project_id"], "app/page.tsx", fixed_code)
    emit_event(
    state["session_id"],
        "Code Fixer Agent",
        "completed",
        "Fixes applied"
    )
    return {
        "retry_count": state["retry_count"] + 1
    }


# from app.agents.reviewer import reviewer_agent
# from app.agents.developer import developer_fix_agent

# from app.tools.file_tools import read_file, write_file


# def fix_project(project_id: str, build_error: str):
#     code = read_file(project_id, "app/page.tsx")
#     instructions = reviewer_agent(code=code, build_error=build_error)
#     fixed_code = developer_fix_agent(code=code, fix_instructions=instructions)
#     write_file(project_id, "app/page.tsx", fixed_code)

#     # return instructions
#     return {
#         "retry_count": state["retry_count"] + 1
#     }