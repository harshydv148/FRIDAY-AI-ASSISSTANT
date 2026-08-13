"""
AI Chat — Groq LLM with optimized token usage.
"""

import os
from groq import Groq, RateLimitError, APIStatusError, APITimeoutError
from dotenv import load_dotenv

from friday.voice import speak, should_speak
from friday.Personality.prompts import get_chat_prompt
from friday.Commands.files import paste_text
from friday.memory import save_conversation_summary

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation = []
MAX_HISTORY = 8

BAD_PHRASES = [
    "no instruction",
    "you haven't provided",
    "please provide",
]

# Session context — temporary, not saved to memory
_session_context = ""


def set_session_context(context: str):
    global _session_context
    _session_context = context


def get_session_context() -> str:
    return _session_context


# Queries that need self-knowledge context
SELF_KNOWLEDGE_TRIGGERS = [
    "how do you",
    "how does your",
    "explain your",
    "what is your",
    "how are you built",
    "your code",
    "your memory",
    "your volume",
    "your intent",
    "your architecture",
    "how do reminders",
    "how do you play",
    "how does friday",
    "your features",
    "what can you",
    "tell me about yourself",
    "how do you work",
    "your implementation",
    "your modules",
    "who are you",
    "introduce yourself",
]


def _needs_self_knowledge(user_input: str) -> bool:
    u = user_input.lower()
    return any(t in u for t in SELF_KNOWLEDGE_TRIGGERS)


def chat(user_input: str, memory: dict) -> str:
    global conversation

    # Current message add karo
    conversation.append({"role": "user", "content": user_input})

    # History trim karo — MAX_HISTORY pairs rakho
    if len(conversation) > MAX_HISTORY * 2:
        conversation = conversation[-(MAX_HISTORY * 2) :]

    # System prompt — self knowledge conditional
    system_prompt = get_chat_prompt(
        memory=memory, include_self_knowledge=_needs_self_knowledge(user_input)
    )

    # Session context inject karo agar available hai
    messages = [{"role": "system", "content": system_prompt}]

    if _session_context:
        messages.append(
            {
                "role": "system",
                "content": f"Current session context: {_session_context}",
            }
        )

    # History add karo — current message already conversation mein hai
    # Isliye conversation[:-1] use karo — last item current user message hai
    # Jo messages list mein separately add ho raha hai
    messages.extend(conversation[:-1])
    messages.append({"role": "user", "content": user_input})

    # Models — fallback order
    models = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b",
    ]

    recoverable_errors = (RateLimitError, APITimeoutError)

    for i, model in enumerate(models):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
            )

            # Token usage log
            usage = response.usage
            print(
                f"📊 [{model}] Prompt: {usage.prompt_tokens} | "
                f"Completion: {usage.completion_tokens} | "
                f"Total: {usage.total_tokens}"
            )

            reply = response.choices[0].message.content
            conversation.append({"role": "assistant", "content": reply})
            return reply

        except recoverable_errors as e:
            # Rate limit ya timeout — next model try karo
            if i < len(models) - 1:
                print(f"⚠️ {model} unavailable ({type(e).__name__}), trying next...")
                continue
            else:
                # Sab models fail ho gaye
                print(f"❌ All models rate limited.")
                return "Rate limit reached boss, try again in a few minutes."

        except APIStatusError as e:
            if e.status_code in (503, 529):
                # Service unavailable — try next
                if i < len(models) - 1:
                    print(f"⚠️ {model} service unavailable, trying next...")
                    continue
            # Other API errors — raise karo
            raise

        except Exception:
            # Programming bugs ya unexpected errors — raise karo
            raise

    return "Something went wrong boss, please try again."


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

    save_conversation_summary(user_input, reply)
    return True
