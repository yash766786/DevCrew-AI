from app.agents.developer import developer_agent

def generator_node(state):

    developer_agent(
        project_id=state["project_id"],
        plan=state["plan"]
    )

    return {
        "generated": True,
        "status": "generated"
    }

