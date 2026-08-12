import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from weather_tool import (
    get_weather,
    get_forecast,
    get_air_quality
)

from search_tool import web_search

from memory import (
    create_database,
    save_message,
    load_messages
)

# LOAD ENVIRONMENT
load_dotenv()

# CREATE DATABASE
create_database()

# GROQ LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# TOOLS
@tool
def weather_tool(city: str):
    """Get current weather information for a city."""
    
    return get_weather(city)


@tool
def forecast_tool(city: str):
    """Get future weather forecast information for a city."""
    
    return get_forecast(city)


@tool
def air_quality_tool(city: str):
    """Get current air quality information for a city."""
    
    return get_air_quality(city)


@tool
def search_tool(query: str):
    """Search the web for current, latest, recent or news information."""
    
    return web_search(query)

# TOOL LIST
tools = [
    weather_tool,
    forecast_tool,
    air_quality_tool,
    search_tool
]

# BIND TOOLS TO LLM
llm_with_tools = llm.bind_tools(tools)

# SYSTEM PROMPT
system_prompt = """
You are a weather assistant.

You can understand:

- English
- Hindi
- Hinglish

Understand the user's intent regardless of how the
question is phrased.

You have access to these tools:

1. weather_tool
   - current weather

2. forecast_tool
   - future weather forecast

3. air_quality_tool
   - current AQI and air quality

4. search_tool
   - latest, recent, news or changing information


TOOL RULES:

- Always use weather_tool for current weather.
- Always use forecast_tool for forecast requests.
- Always use air_quality_tool for AQI or air quality.
- Use search_tool for latest, recent, news or changing information.

- When the user asks for multiple things,
  use all required tools.

- You may call multiple tools for a single question.


CONVERSATION:

Use the conversation history to understand references such as:

- there
- waha
- same city
- same place
- there too
- tomorrow


LOCATION:

Weather tools require an actual city name.

Only pass city names to weather tools.

If the user gives a state or region instead of a city,
ask which city they mean.

Do not directly pass a state name as a city.


LANGUAGE:

- If the user speaks English, respond in English.
- If the user speaks Hindi, respond in Hindi.
- If the user speaks Hinglish, respond naturally in Hinglish.


ANSWER:

- Answer only what the user asks.
- Do not provide unnecessary information.
- Do not provide a full forecast unless the user asks for it.
- Do not claim that you cannot access real-time information.
"""

# AGENT NODE
def agent(state: MessagesState):

    messages = [
        SystemMessage(content=system_prompt)
    ] + state["messages"]

    try:

        response = llm_with_tools.invoke(messages)

        print("TOOL CALLS:", response.tool_calls)

        return {
            "messages": [response]
        }

    except Exception as e:

        print("Agent Error:", e)

        return {
            "messages": []
        }



# TOOL NODE
tool_node = ToolNode(tools)

# CREATE GRAPH
graph = StateGraph(MessagesState)



# ADD NODES
graph.add_node(
    "agent",
    agent
)

graph.add_node(
    "tools",
    tool_node
)

# GRAPH START
graph.add_edge(
    START,
    "agent"
)

# CONDITIONAL ROUTING

graph.add_conditional_edges(
    "agent",
    tools_condition
)

# TOOLS → AGENT
graph.add_edge(
    "tools",
    "agent"
)

# COMPILE GRAPH
app = graph.compile()

# LOAD RECENT MEMORY
old_messages = load_messages()

old_messages = old_messages[-10:]

# CHAT LOOP
while True:

    user_input = input("\nYou: ")    
    # EXIT
    if user_input.lower() in ["exit", "quit"]:

        print("Goodbye!")

        break

    # SAVE USER MESSAGE
    save_message(
        "user",
        user_input
    )

    # BUILD CURRENT CONVERSATION
    current_messages = old_messages + [
        {
            "role": "user",
            "content": user_input
        }
    ]    
    # RUN LANGGRAPH
    try:

        result = app.invoke({
            "messages": current_messages
        })
        
        # GET FINAL MESSAGE
        final_message = result["messages"][-1]

        answer = final_message.content
        
        # SAVE ASSISTANT RESPONSE
        save_message(
            "assistant",
            answer
        )
        
        # UPDATE RECENT MEMORY
        old_messages = load_messages()

        old_messages = old_messages[-10:]
        
        # PRINT ANSWER
        print("Agent:", answer)

    except Exception as e:

        print("Agent Error:", e)

        print(
            "Agent: Sorry, I couldn't process that request right now."
        )