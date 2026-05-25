import os
import time
import webbrowser
from dotenv import load_dotenv

from friday.voice import speak, listen
from friday.state import FridayState
from friday.app_config import USERNAME
from friday.memory import get_memory, should_check_memory, extract_and_save
from friday.Commands.screen import handle_screen_command
from friday.Commands.files import handle_type_command
from friday.Commands.shortcuts import handle_shortcut
from friday.Automation.browser import handle_close_tabs
from friday.Automation.apps import handle_open_command, handle_close_apps
from friday.Automation.system import handle_system_command
from friday.AI.intent import detect_and_handle_intent
from friday.AI.chat import handle_chat
from friday.Commands.screenshot import handle_screenshot_command
from friday.Commands.timer import handle_timer_command
from friday.Commands.notes import handle_notes_command, restore_reminders
from friday.Commands.weather import handle_weather_command
from friday.Commands.todo import handle_todo_command
from friday.Commands.spotify import handle_spotify_command
from friday.Automation.volume import handle_volume_command

load_dotenv()

state = FridayState()

print("FRIDAY online\n")

# Pending reminders restore karo
restore_reminders()

# Voice engine initialize karo
from friday.voice import _init_gemini
_init_gemini()

while True:
    # Standby timeout check
    if state.is_timed_out() and not state.standby:
        state.go_standby()
        print("FRIDAY: (standby mode)")
        speak("Going on standby.")

    user_input = listen()

    if not user_input:
        continue

    print("You:", user_input)

    # WAKE FROM STANDBY
    if state.standby:
        if any(phrase in user_input.lower() for phrase in [
            "friday", "wake up friday",
            "utho friday", "kaam ka waqt",
            "chalo utho friday",
        ]):
            state.wake()
            speak("Back online, boss.")
            continue
        else:
            continue

    # WAKE WORD
    if "friday" in user_input.lower():
        state.wake()

        user_input = user_input.lower().replace("friday", "").strip()

        if not user_input:
            import random
            greetings = [
                "Yeah boss?",
                "Hey! What's up?",
                "I'm here, what do you need?",
                "Listening, boss.",
                "What's good?",
            ]
            speak(random.choice(greetings))
            state.touch()
            continue

    # Active check
    if not state.active:
        continue

    # EXIT
    if user_input.lower().strip() == "exit":
        speak("Later, boss.")
        break

    # GUIDE SESSION — active hai toh pehle handle karo
    from friday.Commands.screen import continue_guide_session
    if continue_guide_session(user_input):
        state.touch()
        continue

    # SCREEN COMMANDS
    if handle_screen_command(user_input):
        state.touch()
        continue

    # MEMORY SAVE
    if should_check_memory(user_input):
        saved = extract_and_save(user_input)
        if saved:
            speak("Got it, noted.")
            state.touch()
            continue

    # SHORTCUTS
    if handle_shortcut(user_input, state):
        state.touch()
        continue

    # TYPE COMMAND
    if handle_type_command(user_input):
        state.touch()
        continue

    # SCREENSHOT
    if handle_screenshot_command(user_input):
        state.touch()
        continue

    # TIMER
    if handle_timer_command(user_input):
        state.touch()
        continue

    # NOTES
    if handle_notes_command(user_input):
        state.touch()
        continue

    # TODO
    if handle_todo_command(user_input):
        state.touch()
        continue

    # WEATHER
    if handle_weather_command(user_input):
        state.touch()
        continue
    
    # OPEN COMMAND
    if handle_open_command(user_input):
        state.touch()
        continue

    # CLOSE TABS
    if handle_close_tabs(user_input):
        state.touch()
        continue

    # CLOSE APPS
    if handle_close_apps(user_input):
        state.touch()
        continue

    if handle_volume_command(user_input):
        state.touch()
        continue
    
    # SPOTIFY/MUSIC
    if handle_spotify_command(user_input):
        state.touch()
        continue

    # SYSTEM COMMANDS
    if handle_system_command(user_input):
        state.touch()
        continue

    # AI INTENT DETECTION
    handled = detect_and_handle_intent(user_input, get_memory())
    if handled:
        state.touch()
        continue

    # NORMAL CONVERSATION
    handle_chat(user_input, get_memory())
    state.touch()