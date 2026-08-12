import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from weather_tool import get_weather , get_forecast , get_air_quality

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
            "description": "Get weather forecast information for a city.",
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
    }
]

messages = [
    {
        "role": "system",
        "content": """You are a weather assistant.
You have access to weather tools.
Always use the available tools when the user asks for
current weather, forecast, or air quality.
Do not say that you cannot access real-time data."""
    },
    {
        "role": "user",
        "content": input("You: ")
    }
]

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message
print("Tool calls:", message.tool_calls)

if message.tool_calls:
    messages.append(message)

    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_weather":
            args = json.loads(tool_call.function.arguments)
            result = get_weather(args["city"])

        elif tool_call.function.name == "get_forecast":
            args = json.loads(tool_call.function.arguments)
            result = get_forecast(args["city"])
        elif tool_call.function.name == "get_air_quality":
            args = json.loads(tool_call.function.arguments)
            result = get_air_quality(args["city"])
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    final_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    print("Agent:", final_response.choices[0].message.content)

else:
    print("Agent:", message.content)