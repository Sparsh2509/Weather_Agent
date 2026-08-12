import os

from dotenv import load_dotenv

from core.graph import app

from core.memory import (
    create_database,
    save_message,
    load_messages
)


load_dotenv()

create_database()


old_messages = load_messages()[-10:]


while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    save_message(
        "user",
        user_input
    )

    current_messages = old_messages + [
        {
            "role": "user",
            "content": user_input
        }
    ]

    try:

        result = app.invoke({
            "messages": current_messages
        })

        answer = result["messages"][-1].content

        save_message(
            "assistant",
            answer
        )

        old_messages = load_messages()[-10:]

        print("Agent:", answer)

    except Exception as e:

        print("Agent Error:", e)

        print(
            "Agent: Sorry, I couldn't process that request right now."
        )