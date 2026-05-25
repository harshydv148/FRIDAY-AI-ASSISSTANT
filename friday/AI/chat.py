"""
Normal AI conversation — memory-aware responses.
"""

import os
from groq import Groq
from dotenv import load_dotenv

from friday.voice import speak, should_speak
from friday.Personality.prompts import get_chat_prompt
from friday.Commands.files import paste_text
from friday.memory import (
    get_memory, should_check_memory, extract_and_save,
    save_conversation_summary, get_conversation_history,
)


load_dotenv()
load_dotenv()

from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Conversation history
conversation = [
    {
        "role": "system",
        "content": "You are FRIDAY, a smart female AI assistant.",
    }
]

MAX_HISTORY = 10

BAD_PHRASES = [
    "no instruction",
    "you haven't provided",
    "please provide",
]


def chat(user_input: str, memory: dict) -> str:
    global conversation

    conversation.append({"role": "user", "content": user_input})
    if len(conversation) > MAX_HISTORY + 1:
        conversation = [conversation[0]] + conversation[-(MAX_HISTORY):]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": get_chat_prompt(memory),
            },
            {
                "role": "system",
                "content": "ABSOLUTE RULE: Respond in English only. Never use Hindi, Urdu, or Hinglish. Not even one word.",
            },
            *conversation[1:],
        ],
    )

    reply = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": reply})
    return reply
def handle_chat(user_input: str, memory: dict) -> bool:
    reply = chat(user_input, memory)

    if any(phrase in reply.lower() for phrase in BAD_PHRASES):
        print("⚠️ Ignored useless reply")
        return True

    if should_speak(reply):
        speak(reply)

    if "write" in user_input.lower() or "type" in user_input.lower():
        import time
        time.sleep(1)
        paste_text(reply)

    # Conversation history save karo
    save_conversation_summary(user_input, reply)

    return True