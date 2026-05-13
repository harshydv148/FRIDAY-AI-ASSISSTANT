"""
Normal AI conversation — memory-aware responses.
"""

import os
from groq import Groq
from dotenv import load_dotenv

from friday.voice import speak, should_speak
from friday.Personality.prompts import get_chat_prompt
from friday.Commands.files import paste_text

load_dotenv()
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
    """
    Normal conversation handle karo.
    Returns FRIDAY ka reply.
    """
    global conversation

    # History mein add karo
    conversation.append({"role": "user", "content": user_input})

    # History limit
    if len(conversation) > MAX_HISTORY + 1:
        conversation = [conversation[0]] + conversation[-(MAX_HISTORY):]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": get_chat_prompt(memory),
            },
            *conversation[1:],  # system prompt skip karo, apna daal raha hai
        ],
    )

    reply = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": reply})
    return reply


def handle_chat(user_input: str, memory: dict) -> bool:
    """
    Normal conversation handle karo.
    Returns True hamesha — yeh last fallback hai.
    """
    reply = chat(user_input, memory)
    print("FRIDAY:", reply)

    # Useless replies block karo
    if any(phrase in reply.lower() for phrase in BAD_PHRASES):
        print("FRIDAY: (ignored useless reply)")
        return True

    if should_speak(reply):
        speak(reply)

    # Agar user ne type/write kaha toh paste karo
    if "write" in user_input.lower() or "type" in user_input.lower():
        import time
        time.sleep(1)
        paste_text(reply)

    return True