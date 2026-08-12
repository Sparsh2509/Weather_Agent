import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from weather_tool import (
    get_weather,
    get_forecast,
    get_air_quality
)

from memory import (
    create_database,
    save_message,
    load_messages,
    save_summary,
    load_summary
)

from search_tool import web_search


# =========================
# LOAD ENVIRONMENT
# =========================

load_dotenv()


# =========================
# GROQ CLIENT
# =========================

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# =========================
# TOOLS
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },
                "required": ["city"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "Get future weather forecast for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },
                "required": ["city"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_air_quality",
            "description": "Get current air quality information for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },
                "required": ["city"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current, latest, recent or news information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# =========================
# DATABASE
# =========================

create_database()


# =========================
# SYSTEM PROMPT
# =========================

system_message = {
    "role": "system",
    "content": """
You are a weather assistant.

You have access to these tools:

1. get_weather - current weather
2. get_forecast - future weather forecast
3. get_air_quality - current air quality
4. web_search - latest, recent, news or changing information

Rules:

- Always use get_weather for current weather.
- Always use get_forecast for future weather.
- Always use get_air_quality for AQI.
- Use web_search for latest, recent, news or changing information.
- When the user asks for multiple things, use all required tools.
- You can call multiple tools when necessary.
- Use conversation history to understand words like:
  'there', 'waha', 'same city', 'tomorrow', 'there too'.
- Only pass actual city names to weather tools.
- Do not claim that you cannot access real-time information.
"""
}


# =========================
# LOAD PREVIOUS MEMORY
# =========================

messages = [system_message]

# Load old conversation summary
summary = load_summary()

if summary:
    messages.append({
        "role": "system",
        "content": f"""
Previous conversation summary:

{summary}

Use this summary only when it is relevant to the current conversation.
"""
    })


# Load only recent messages
old_messages = load_messages()

old_messages = old_messages[-10:]

messages.extend(old_messages)


# =========================
# CHAT LOOP
# =========================

while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break


    # =========================
    # SAVE USER MESSAGE
    # =========================

    messages.append({
        "role": "user",
        "content": user_input
    })

    save_message(
        "user",
        user_input
    )


    # =====================================================
    # AGENT LOOP
    # =====================================================

    while True:

        # =========================
        # ASK LLM
        # =========================

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

        except Exception as e:

            print("Agent Error:", e)

            print(
                "Agent: Sorry, I couldn't process that request right now."
            )

            break

        message = response.choices[0].message
        print("TOOL CALLS:", message.tool_calls)


        # =========================
        # CHECK TOOL CALLS
        # =========================

        if not message.tool_calls:

            # LLM has final answer
            answer = message.content

            messages.append({
                "role": "assistant",
                "content": answer
            })

            save_message(
                "assistant",
                answer
            )

            print("Agent:", answer)

            break


        # =========================
        # ADD ASSISTANT TOOL CALL
        # =========================

        messages.append(message)


        # =========================
        # EXECUTE ALL TOOL CALLS
        # =========================

        for tool_call in message.tool_calls:

            try:

                args = json.loads(
                    tool_call.function.arguments
                )


                # -------------------------
                # WEATHER
                # -------------------------

                if tool_call.function.name == "get_weather":

                    result = get_weather(
                        args["city"]
                    )


                # -------------------------
                # FORECAST
                # -------------------------

                elif tool_call.function.name == "get_forecast":

                    result = get_forecast(
                        args["city"]
                    )


                # -------------------------
                # AIR QUALITY
                # -------------------------

                elif tool_call.function.name == "get_air_quality":

                    result = get_air_quality(
                        args["city"]
                    )


                # -------------------------
                # WEB SEARCH
                # -------------------------

                elif tool_call.function.name == "web_search":

                    result = web_search(
                        args["query"]
                    )


                # -------------------------
                # UNKNOWN TOOL
                # -------------------------

                else:

                    result = {
                        "error": "Unknown tool"
                    }


            except Exception as e:

                result = {
                    "error": str(e)
                }


            # =========================
            # CONVERT RESULT TO JSON
            # =========================

            tool_result = json.dumps(
                result
            )


            # =========================
            # SEND TOOL RESULT TO LLM
            # =========================

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })


    # =====================================================
    # AGENT LOOP ENDS HERE
    # =====================================================