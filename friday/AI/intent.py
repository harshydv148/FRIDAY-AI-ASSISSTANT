"""
AI Intent Detection — user input se action extract karna.
"""

import os
import json
import webbrowser
from groq import Groq
from dotenv import load_dotenv

from friday.voice import speak
from friday.Personality.prompts import INTENT_PROMPT
from friday.app_config import (
    WEB_APPS, SYSTEM_APPS, BROWSER_APPS,
    APP_FIRST, common_apps,
)
from friday.Automation.apps import (
    open_app, close_specific_window, close_all_apps, close_specific_apps,
)
from friday.Automation.browser import (
    close_all_tabs, close_current_tab, close_current_window,
)
from friday.Commands.screen import handle_professional_screen
from friday.Commands.files import find_file, find_app

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def detect_and_handle_intent(user_input: str, memory: dict) -> bool:
    """
    AI se intent detect karo aur handle karo.
    Returns True agar koi action handle hua.
    Returns False agar normal conversation chahiye.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )

        reply = response.choices[0].message.content.strip()
        reply = reply.replace("```json", "").replace("```", "").strip()

        start = reply.find("{")
        end = reply.rfind("}") + 1
        if start == -1 or end == 0:
            return False

        reply = reply[start:end]
        data = json.loads(reply)

        action = data.get("action")
        target = data.get("target")

        # OPEN
        if action == "open" and target:
            target = target.lower().strip()
            open_app(target)
            return True

        # CLOSE TAB
        elif action == "close_tab":
            close_current_tab()
            return True

        # CLOSE WINDOW
        elif action == "close_window":
            if target:
                close_specific_window(target)
            else:
                close_current_window()
            return True

        # CLOSE ALL TABS
        elif action == "close_all_tabs":
            close_all_tabs()
            return True

        # CLOSE ALL APPS
        elif action == "close_all_apps":
            if target:
                keep_apps = [
                    app.strip()
                    for app in target
                    .replace(" and ", ",")
                    .replace(" or ", ",")
                    .split(",")
                    if app.strip()
                ]
                close_specific_apps(keep_apps)
            else:
                close_all_apps()
            return True

        # SEARCH
        elif action == "search" and target:
            if target.strip().lower() == "search":
                speak("What do you want to search for, boss?")
                return True
            url = f"https://www.google.com/search?q={target}"
            webbrowser.open(url)
            speak(f"Searching for {target}, boss.")
            return True

        # MAKE PROFESSIONAL
        elif action == "make_professional":
            handle_professional_screen()
            return True

        elif action == "log_feature" and target:
            from friday.Personality.self_knowledge import log_new_feature
            log_new_feature(target)
            speak(f"Got it boss, I'll remember that you added {target}.")
            return True
        
        elif action == "solve_screen":
            from friday.Commands.screen import handle_screen_command
            handle_screen_command("solve screen")
            return True

        elif action == "guide_screen":
            from friday.Commands.screen import handle_screen_command
            handle_screen_command("help me solve")
            return True
        
        # NONE — normal conversation chahiye
        elif action == "none" or not action:
            return False
        
    except Exception as e:
        print(f"Intent error: {e}")

    return False