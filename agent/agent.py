import os

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

from langgraph.graph import MessagesState

from agent.tools import tools
from agent.prompts import SYSTEM_PROMPT


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


llm_with_tools = llm.bind_tools(tools)


def agent(state: MessagesState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    print("TOOL CALLS:", response.tool_calls)

    return {
        "messages": [response]
    }