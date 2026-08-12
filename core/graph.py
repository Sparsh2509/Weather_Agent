from langgraph.graph import (
    StateGraph,
    MessagesState,
    START
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition
)

from core.agent import agent
from core.tools import tools


graph = StateGraph(MessagesState)


graph.add_node(
    "agent",
    agent
)

graph.add_node(
    "tools",
    ToolNode(tools)
)


graph.add_edge(
    START,
    "agent"
)


graph.add_conditional_edges(
    "agent",
    tools_condition
)


graph.add_edge(
    "tools",
    "agent"
)


app = graph.compile()