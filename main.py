import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from weather_tool import get_weather, get_forecast, get_air_quality
from memory import create_database, save_message, load_messages

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
                    "city": {"type": "string"}
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
                    "city": {"type": "string"}
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
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    }
]

# MEMORY
create_database()

messages = [
    {
        "role": "system",
        "content": """You are a weather assistant.
You have access to weather tools.

Always use the available tools when the user asks for
current weather, forecast, or air quality.

Use conversation history to understand references like
'there', 'tomorrow', 'the same city', or 'there too'.

Only pass actual city names to the weather tools.
If the user provides a state or region instead of a city,
ask which city they mean.

Do not say that you cannot access real-time data."""
    }
]

messages.extend(load_messages())

while True:

    user_input = input("\nYou: ")
    save_message("user", user_input)

    messages.append({
        "role": "user",
        "content": user_input
    })

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Add user message to memory
    messages.append({
        "role": "user",
        "content": user_input
    })

    # First LLM call
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:

        # Save assistant's tool-call message
        messages.append(message)

        for tool_call in message.tool_calls:

            args = json.loads(tool_call.function.arguments)

            if tool_call.function.name == "get_weather":
                result = get_weather(args["city"])

            elif tool_call.function.name == "get_forecast":
                result = get_forecast(args["city"])

            elif tool_call.function.name == "get_air_quality":
                result = get_air_quality(args["city"])

            # Save tool result in memory
            tool_result = json.dumps(result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

            save_message(
                "tool",
                tool_result,
                tool_call.id
            )

        # Final LLM response
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        answer = final_response.choices[0].message.content

        # Save final assistant response in memory
        messages.append({
            "role": "assistant",
            "content": answer
        })

        print("Agent:", answer)
        save_message("assistant", answer)

    else:

        messages.append({
            "role": "assistant",
            "content": message.content
        })

        print("Agent:", message.content)