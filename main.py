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
    load_messages
)

from search_tool import web_search

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

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
                        "type": "string"
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
            "description": "Get weather forecast information for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string"
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
                        "type": "string"
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
            "description": "Search the web for current or latest information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# ---------------- DATABASE ----------------

create_database()


# ---------------- SYSTEM PROMPT ----------------

system_message = {
    "role": "system",
    "content": """You are a weather assistant.

You have access to these tools:

1. get_weather - current weather
2. get_forecast - future weather forecast
3. get_air_quality - current air quality
4. web_search - latest or recent information from the web

Always use get_weather for current weather.
Always use get_forecast for forecasts.
Always use get_air_quality for AQI.
Use web_search for latest, recent, news, or changing information.

When a user asks for multiple things, you may call multiple tools.
For example, if the user asks for current weather and latest weather news,
call both get_weather and web_search.

Use conversation history to understand references like
'there', 'tomorrow', 'same city', or 'there too'.

Only pass actual city names to weather tools.

Do not say that you cannot access real-time data."""
}


# ---------------- LOAD MEMORY ----------------

messages = [system_message]

old_messages = load_messages()

messages.extend(old_messages)


# ---------------- CHAT LOOP ----------------

while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break


    # Save user message
    messages.append({
        "role": "user",
        "content": user_input
    })

    save_message(
        role="user",
        content=user_input
    )


    # ---------------- FIRST LLM CALL ----------------

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message
    print("TOOL CALLS:", message.tool_calls)


    # ---------------- TOOL CALL ----------------

    if message.tool_calls:

        # Convert assistant message into dictionary
        assistant_message = {
            "role": "assistant",
            "content": message.content
        }

        tool_calls_for_memory = []

        for tool_call in message.tool_calls:

            tool_call_data = {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            }

            tool_calls_for_memory.append(tool_call_data)

        assistant_message["tool_calls"] = tool_calls_for_memory

        messages.append(assistant_message)

        save_message(
            role="assistant",
            content=message.content,
            tool_calls=tool_calls_for_memory
        )


        # ---------------- EXECUTE TOOLS ----------------

        for tool_call in message.tool_calls:

            args = json.loads(
                tool_call.function.arguments
            )

            if tool_call.function.name == "get_weather":

                result = get_weather(
                    args["city"]
                )

            elif tool_call.function.name == "get_forecast":

                result = get_forecast(
                    args["city"]
                )

            elif tool_call.function.name == "get_air_quality":

                result = get_air_quality(
                    args["city"]
                )
            elif tool_call.function.name == "web_search":
                result = web_search(
                    args["query"])

            else:

                result = {
                    "error": "Unknown tool"
                }


            # Convert result to JSON
            tool_result = json.dumps(result)


            # Add to current context
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })


            # Save tool result
            save_message(
                role="tool",
                content=tool_result,
                tool_call_id=tool_call.id
            )


        # ---------------- FINAL LLM CALL ----------------

        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        answer = final_response.choices[0].message.content


        # Add final answer to context
        messages.append({
            "role": "assistant",
            "content": answer
        })


        # Save final answer
        save_message(
            role="assistant",
            content=answer
        )


        print("Agent:", answer)


    else:

        # No tool required
        messages.append({
            "role": "assistant",
            "content": message.content
        })

        save_message(
            role="assistant",
            content=message.content
        )

        print("Agent:", message.content)