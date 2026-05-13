"""
Quick commands — time, date, greetings, study mode.
"""

import os
import webbrowser
from datetime import datetime

from friday.voice import speak


def handle_greeting(user_input: str) -> bool:
    u = user_input.lower().strip()

    if u in ["hello", "hi", "hey"]:
        speak("Hello boss!")
        return True

    if "good morning" in u:
        speak("Good morning boss! Hope you're ready to conquer the day.")
        return True

    if "good evening" in u:
        speak("Good evening boss! What are we working on tonight?")
        return True

    if "good night" in u:
        speak("Good night boss! Get some rest.")
        return True

    if "good afternoon" in u:
        speak("Good afternoon boss! What can I do for you?")
        return True

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


def handle_shortcut(user_input: str) -> bool:
    """
    Sab shortcut commands ek jagah check karo.
    Returns True agar koi command handle hua.
    """
    if handle_greeting(user_input):
        return True
    if handle_time(user_input):
        return True
    if handle_date(user_input):
        return True
    if handle_study_mode(user_input):
        return True
    return False