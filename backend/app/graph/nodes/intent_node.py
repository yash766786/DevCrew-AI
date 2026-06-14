from app.agents.intent_agent import intent_agent


def intent_node(state):
    result = intent_agent(state["human_message"])

    return {
        "action": result["action"]
    }