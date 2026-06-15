# app/graph/respond_graph.py
from langgraph.graph import StateGraph, END
from app.graph.state import ProjectState
from app.graph.nodes.intent_node  import intent_node 
from app.graph.nodes.scope_node import scope_node
from app.graph.nodes.plan_editor_node import plan_editor_node
from app.graph.routers import intent_router, modification_scope_router


builder = StateGraph(ProjectState)

builder.add_node("intent", intent_node)
builder.add_node("scope", scope_node)
builder.add_node("plan_editor", plan_editor_node)

builder.set_entry_point("intent")

builder.add_conditional_edges("intent", intent_router)
builder.add_conditional_edges("scope", modification_scope_router)
builder.add_edge("plan_editor", END)

respond_graph = builder.compile()