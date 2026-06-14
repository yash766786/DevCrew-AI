from app.tools.file_tools import read_file, write_file
from app.agents.developer import developer_fix_agent

def fix_node(state):
    code = read_file(state["project_id"], "app/page.tsx")

    fixed_code = developer_fix_agent(code, state["fix_instructions"])

    write_file(state["project_id"], "app/page.tsx", fixed_code)

    return {
        "retry_count": state["retry_count"] + 1
    }