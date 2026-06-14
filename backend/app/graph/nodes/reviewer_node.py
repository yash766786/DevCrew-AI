from app.tools.file_tools import read_file
from app.agents.reviewer import reviewer_agent

def reviewer_node(state):
    code = read_file(state["project_id"], "app/page.tsx")
    instructions = reviewer_agent(code, state["build_error"])

    return {
        "fix_instructions": instructions
    }