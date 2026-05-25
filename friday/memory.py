import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MEMORY_FILE = "memory.json"


def load_memory() -> dict:
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_memory(memory: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


memory = load_memory()


def refresh_memory():
    global memory
    memory = load_memory()


def get_memory() -> dict:
    return memory

def delete_memory_key(key: str) -> bool:
    """Memory se ek key delete karo."""
    global memory
    memory = load_memory()
    if key in memory:
        del memory[key]
        save_memory(memory)
        refresh_memory()
        print(f"🗑️ Deleted memory: {key}")
        return True
    return False

explicit_keywords = [
    "remember", "yaad rakh", "save this", "note this",
    "save karo", "yaad karo", "remember this", "store this",
    "isey yaad rkhna", "yeh save karo",
]

personal_hints= [
    "my ", "mera ", "meri ", "i am ", "i'm ", "main hoon",
    "mera naam", "my name", "my age", "i live",
    "i like ", "i love ", "i hate ", "i enjoy ", "i prefer ",
    "my favourite", "my favorite", "mujhe pasand", "mujhe nahi pasand",
    "i study", "i work", "i am a", "main ek",
    "my hobby", "my goal", "i want to", "i use",
    "my city", "my college", "my school", "i play", "i watch",
    "mera favourite", "meri favourite", "mujhe ", "i don't like",
]

MEMORY_PROMPT = """
You are a memory extraction engine for a personal AI assistant.

Your ONLY job: decide if this message contains a personal fact about the user.

ALWAYS SAVE these patterns (save: true):
- "I like X" → favourite or preference
- "I love X" → favourite or preference
- "I hate X" → dislike
- "I enjoy X" → hobby or preference
- "I play X" → hobby
- "I watch X" → hobby
- "I am X years old" → age
- "I am a X" → education or job
- "I work at X" → job
- "I live in X" → city
- "My name is X" → name
- "I study X" → education
- "My favourite X is Y" → favourite_X
- "I prefer X" → preference
- "mujhe X pasand hai" → favourite or preference
- "mera X hai" → personal info
- "remember X" → whatever X is

NEVER SAVE:
- Pure questions ("what is", "how to", "why")
- Commands ("open", "search", "play")
- Random numbers with no context ("14", "2006")
- General knowledge ("what is python")

KEY NAMING - always specific:
- like/love food → "favourite_food"
- like/love sport → "favourite_sport"
- like/love music/artist/song → "favourite_music"
- like/love movie → "favourite_movie"
- like/love colour → "favourite_colour"
- like/love game → "favourite_game"
- hobby/enjoy/play → "hobby"
- age → "age"
- city/live in → "city"
- name → "name"
- job/work → "job"
- education/student → "education"
- hate/dislike → "dislike"

Examples:
"I like burger" → {"save": true, "key": "favourite_food", "value": "burger"}
"I like burgers" → {"save": true, "key": "favourite_food", "value": "burger"}
"I love cricket" → {"save": true, "key": "favourite_sport", "value": "cricket"}
"I am 19 years old" → {"save": true, "key": "age", "value": "19"}
"I am a BCA student" → {"save": true, "key": "education", "value": "BCA student"}
"open youtube" → {"save": false}
"what is python" → {"save": false}
"2006" → {"save": false}
"I like playing games" → {"save": true, "key": "hobby", "value": "playing games"}

Return ONLY valid JSON. No explanation. No extra text.
"""


def should_check_memory(user_input: str) -> bool:
    """Check karo ki memory extraction zaroori hai ya nahi"""
    u = user_input.lower().strip()
    if any(kw in u for kw in explicit_keywords):
        return True
    if any(hint in u for hint in personal_hints):
        return True
    return False


def extract_and_save(user_input: str) -> bool:
    """
    Memory extract karo aur save karo.
    Returns True agar kuch save hua, False otherwise.
    """
    global memory

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": MEMORY_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )

    mem_reply = response.choices[0].message.content.strip()
    mem_reply = mem_reply.replace("```json", "").replace("```python", "").replace("```", "")

    start = mem_reply.find("{")
    end = mem_reply.rfind("}") + 1
    if start == -1 or end == 0:
        return False

    mem_reply = mem_reply[start:end].strip()

    try:
        data = json.loads(mem_reply)
        save_flag = data.get("save")
        key = data.get("key")
        value = data.get("value")

        if save_flag and key and value and len(value) <= 100:
            memory[key] = value
            save_memory(memory)
            refresh_memory()
            print(f"🧠 Saved: {key} = {value}")
            return True

    except Exception as e:
        print(f"MEMORY ERROR: {e}")

    return False


CONVERSATION_MEMORY_KEY = "__conversation_history__"
MAX_CONVERSATIONS_STORED = 20


def save_conversation_summary(user_input: str, friday_reply: str):
    """
    Har conversation turn ka summary memory mein save karo.
    """
    from datetime import datetime
    global memory

    memory = load_memory()
    history = memory.get(CONVERSATION_MEMORY_KEY, [])

    entry = {
        "time": datetime.now().strftime("%d %b %Y %H:%M"),
        "user": user_input,
        "friday": friday_reply,
    }

    history.append(entry)

    # Sirf last 20 conversations rakho
    memory[CONVERSATION_MEMORY_KEY] = history[-MAX_CONVERSATIONS_STORED:]
    save_memory(memory)


def get_conversation_history() -> str:
    """
    Previous conversations ka readable summary return karo.
    """
    memory = load_memory()
    history = memory.get(CONVERSATION_MEMORY_KEY, [])

    if not history:
        return "No previous conversations."

    lines = []
    for entry in history[-10:]:  # last 10 conversations
        lines.append(
            f"[{entry['time']}] User: {entry['user']} → FRIDAY: {entry['friday']}"
        )

    return "\n".join(lines)


def clear_conversation_history():
    """
    Conversation history clear karo.
    """
    global memory
    memory = load_memory()
    memory[CONVERSATION_MEMORY_KEY] = []
    save_memory(memory)
    print("🗑️ Conversation history cleared.")