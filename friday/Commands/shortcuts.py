"""
Quick commands — time, date, greetings, study mode.
"""

import os
import webbrowser
from datetime import datetime

from friday.voice import speak


def handle_greeting(user_input: str) -> bool:
    # u = user_input.lower().strip()

    # if u in ["hello", "hi", "hey"]:
    #     speak("Hello boss!")
    #     return True

    # if "good morning" in u:
    #     speak("Good morning boss! Hope you're ready to conquer the day.")
    #     return True

    # if "good evening" in u:
    #     speak("Good evening boss! What are we working on tonight?")
    #     return True

    # if "good night" in u:
    #     speak("Good night boss! Get some rest.")
    #     return True

    # if "good afternoon" in u:
    #     speak("Good afternoon boss! What can I do for you?")
    #     return True

    return False


def handle_time(user_input: str) -> bool:
    time_triggers = [
        "time", "what time", "current time", "kitne baje",
        "time kya", "kya time", "time kya hai", "time kya hua",
        "time batao", "time bolo", "abhi kitne baje hain",
        "what's the time", "baje hain",
    ]
    if any(t in user_input.lower() for t in time_triggers):
        now = datetime.now()
        hour = now.strftime("%I")
        minute = now.strftime("%M")
        ampm = now.strftime("%p")
        speak(f"It's {hour}:{minute} {ampm}, boss.")
        return True
    return False


def handle_date(user_input: str) -> bool:
    if "day" in user_input.lower() or "date" in user_input.lower():
        now = datetime.now()
        day = now.strftime("%A")
        date = now.strftime("%d %B %Y")
        speak(f"Today is {day}, {date}, boss.")
        return True
    return False


STUDY_LINKS = os.getenv(
    "STUDY_LINKS",
    "https://leetcode.com,https://chat.openai.com,https://github.com"
).split(",")


def handle_study_mode(user_input: str) -> bool:
    if "study mode" in user_input.lower():
        speak("Activating study mode, boss.")
        for link in STUDY_LINKS:
            webbrowser.open_new_tab(link.strip())
        return True
    return False


def handle_standby(user_input: str, state) -> bool:
    standby_triggers = [
        "standby", "stand by", "so jao", "so ja",
        "rest karo", "band ho jao", "chup ho jao",
        "standby mode", "go to standby",
        "standby pr jao", "standby mein jao",
    ]
    u = user_input.lower().strip()

    if any(t in u for t in standby_triggers):
        # Auto standby toggle
        if "auto standby band" in u or "auto standby off" in u:
            state.auto_standby = False
            speak("Auto standby off boss.")
            return True

        if "auto standby on" in u or "auto standby chalu" in u:
            state.auto_standby = True
            speak("Auto standby on boss.")
            return True

        # Manual standby
        state.go_standby()
        speak("Going on standby mode sir.")
        print("FRIDAY: (standby mode)")
        return True

    return False


def handle_shortcut(user_input: str, state=None) -> bool:
    u = user_input.lower().strip()
    if state and handle_standby(user_input, state):
        return True
    
    # Clear conversation history
    if any(t in user_input.lower() for t in [
        "clear history", "history clear karo",
        "purani baatein bhool jao", "conversation clear"
    ]):
        from friday.memory import clear_conversation_history
        clear_conversation_history()
        speak("Done boss, I've cleared our conversation history.")
        return True
    if handle_greeting(user_input):
        return True
    if handle_time(user_input):
        return True
    if handle_date(user_input):
        return True
    if handle_study_mode(user_input):
        return True
    # Memory delete
    delete_triggers = [
        "delete it", "delete this", "forget it",
        "remove it", "delete favourite", "remove this",
        "delete memory", "forget this",
    ]
    if any(t in u for t in delete_triggers):
        from friday.memory import get_memory, delete_memory_key
        mem = get_memory()

        # Last mentioned key dhundho — ya AI se puchho
        # Simple approach — last conversation se key guess karo
        speak("Which info should I delete, boss? Be specific.")
        return True

    # Specific delete — "delete my favourite game"
    if "delete" in u or "remove" in u or "forget" in u:
        from friday.memory import get_memory, delete_memory_key
        mem = get_memory()

        # Key extract karo
        for key in mem.keys():
            if key.replace("_", " ") in u or key in u:
                delete_memory_key(key)
                speak(f"Deleted {key.replace('_', ' ')}, boss.")
                return True

        # Koi key nahi mili
        if any(t in u for t in ["delete", "remove", "forget"]):
            speak("What exactly should I forget, boss?")
            return True

    return False
