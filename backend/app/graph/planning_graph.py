# app/graph/planning_graph.py
from langgraph.graph import StateGraph, END
from app.graph.state import ProjectState
from app.graph.nodes.scope_node import scope_node
from app.graph.nodes.planner_node import planner_node
from app.graph.routers import scope_router



builder = StateGraph(ProjectState)

builder.add_node("scope", scope_node)
builder.add_node("planner", planner_node)

builder.set_entry_point("scope")

builder.add_conditional_edges("scope", scope_router)
builder.add_edge("planner", END)

planning_graph = builder.compile()