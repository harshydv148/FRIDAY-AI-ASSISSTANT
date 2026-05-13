import os
from dotenv import load_dotenv
import time
import webbrowser

from friday.memory import get_memory, should_check_memory, extract_and_save
from friday.Commands.files import handle_type_command
from friday.Automation.browser import handle_close_tabs
from friday.Automation.apps import handle_open_command, handle_close_apps

from friday.voice import speak, listen
from friday.state import FridayState
from friday.Commands.screen import handle_screen_command
from friday.Commands.shortcuts import handle_shortcut
from friday.Automation.system import handle_system_command
from friday.AI.intent import detect_and_handle_intent
from friday.AI.chat import handle_chat

state = FridayState()

# Load environment variables
load_dotenv()
print("FRIDAY (type 'exit' to quit)\n")


while True:
    if state.is_timed_out() and not state.standby:
        state.go_standby()
        print("FRIDAY: (standby mode)")
        speak("Going on standby, Sir.")

    user_input = listen()

    if not user_input:
        continue

    # state.touch()
    print("You:", user_input)

    #  WAKE FROM STANDBY
    if state.standby:
        if any(
            phrase in user_input.lower()
            for phrase in [
                "friday",
                "wake up friday",
                "utho friday",
                "kaam ka waqt",
                "chalo utho friday",
            ]
        ):
            state.wake()
            speak("Aapke liye hamesha, boss.")
            print("FRIDAY: Aapke liye hamesha boss")
            continue
        else:
            continue

    #  WAKE WORD RESPONSE
    if "friday" in user_input.lower():
        state.wake()
        if state.first_start:
            speak("Greeting boss, aaj kya krne ka plan hai.")
            print("FRIDAY: Greeting boss, aaj kya krne ka plan hai")
            state.first_start = False
        else:
            speak("Yes boss, I'm listening.")
            print("FRIDAY: Yes boss, I'm listening")

        # remove wake word
        user_input = user_input.lower().replace("friday", "").strip()

        if not user_input:
            continue

    #  agar active nahi hai → ignore
    if not state.active:
        continue


    # SCREEN COMMANDS
    if handle_screen_command(user_input):
        state.touch()
        continue


    if user_input.lower().strip() == "exit":
        speak("Goodbye, sir.")
        print("FRIDAY: Goodbye, sir.")
        break

    #  AUTO MEMORY SAVE
    if should_check_memory(user_input):
        saved = extract_and_save(user_input)
        if saved:
            speak(f"Got it boss, noted.")
            continue

    #  update active time (VERY IMPORTANT)
    state.touch()

    # if user_input.lower() == "exit":
    #     speak("Goodbye, sir.")
    #     print("FRIDAY: Goodbye, sir.")
    #     break

    # -----commands start -------------------------------------------

    if handle_type_command(user_input):
        state.touch()
        continue
    
    #shortcut hi , hello , gm -:
    if handle_shortcut(user_input):
        state.touch()
        continue
    # ---------Websiteee search commands--------->
    #opening app file handling 
    if handle_open_command(user_input):
        state.touch()
        continue

    # OS commands 
    # tabs closing handling 
    if handle_close_tabs(user_input):
        state.touch()
        continue

    # CLOSE ALL APPS - except VS Code aur terminal
    if handle_close_apps(user_input):
        state.touch()
        continue

    if handle_system_command(user_input):
        state.touch()
        continue

    # ---------COMMANDS over --------

    # AI INTENT DETECTION - Natural language mei 
    handled = detect_and_handle_intent(user_input, get_memory())
    if handled:
        state.touch()
        continue

    # Normal AI conversation — last fallback
    handle_chat(user_input, get_memory())
    state.touch()