# from app.agents.developer import developer_agent

# def generator_node(state):
#     developer_agent(project_id=state["project_id"], plan=state["plan"])

#     return {
#         "generated": True,
#         "status": "generated"
#     }


from app.services.workspace import create_workspace
from app.services.scaffold import scaffold_project
from app.agents.developer import developer_agent
from app.websocket.events import emit_event

def generator_node(state):
    emit_event(
        state["session_id"],
        "Code Generator Agent",
        "running",
        "Generating application code..."
    )

    create_workspace(state["project_id"])
    scaffold_project(state["project_id"])
    developer_agent(state["project_id"], state["plan"])
    
    emit_event(
        state["session_id"],
        "Code Generator Agent",
        "completed",
        "Application code generated"
    )

    return {
        "generated": True,
        "status": "generated"
    }