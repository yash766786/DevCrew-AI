# app/graph/execution_graph.py
from langgraph.graph import StateGraph, END
from app.graph.state import ProjectState
from app.graph.routers import build_router

from app.graph.nodes.generator_node import generator_node
from app.graph.nodes.build_node import build_node
from app.graph.nodes.reviewer_node import reviewer_node
from app.graph.nodes.fix_node import fix_node
from app.graph.nodes.preview_node import preview_node


builder = StateGraph(ProjectState)

builder.add_node("generator", generator_node)
builder.add_node("build", build_node)
builder.add_node("reviewer", reviewer_node)
builder.add_node("fix",fix_node)
builder.add_node("preview", preview_node)

builder.set_entry_point("generator")

builder.add_edge("generator", "build")
builder.add_conditional_edges("build",build_router)
builder.add_edge("reviewer", "fix")
builder.add_edge("fix", "build")
builder.add_edge("preview", END)

execution_graph = builder.compile()