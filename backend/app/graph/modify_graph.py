from langgraph.graph import StateGraph, START, END
from app.graph.state import ProjectState
from app.graph.nodes.modify_intent_node import modify_intent_node
from app.graph.nodes.scope_node import scope_node
from app.graph.nodes.editor_node import editor_node
from app.graph.nodes.satisfaction_node import satisfaction_node
from app.graph.nodes.build_node import build_node
from app.graph.nodes.reviewer_node import reviewer_node
from app.graph.nodes.fix_node import fix_node
from app.graph.nodes.preview_node import preview_node
from app.graph.routers import modify_intent_router, modify_scope_router, build_router

builder = StateGraph(ProjectState)

builder.add_node("intent", modify_intent_node)
builder.add_node("scope", scope_node)
builder.add_node("editor", editor_node)
builder.add_node("satisfaction", satisfaction_node)
builder.add_node("build", build_node)
builder.add_node("reviewer", reviewer_node)
builder.add_node("fixer", fix_node)
builder.add_node("preview", preview_node)

builder.add_edge(START, "intent")
builder.add_conditional_edges("intent", modify_intent_router, {
    "satisfaction": "satisfaction",
    "scope": "scope"
})

builder.add_conditional_edges("scope", modify_scope_router,{
    "editor": "editor",
    END: END
})

builder.add_edge("editor", "build")

builder.add_conditional_edges("build", build_router,{
    "preview": "preview",
    "reviewer": "reviewer",
    END: END
})

builder.add_edge("reviewer", "fixer")
builder.add_edge("fixer", "build")
builder.add_edge("preview", END)
builder.add_edge("satisfaction", END)

modify_graph = builder.compile()