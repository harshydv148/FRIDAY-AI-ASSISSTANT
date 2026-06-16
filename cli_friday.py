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
from friday.Commands.git_commands import handle_git_command
from friday.Commands.network import handle_network_command
from friday.Commands.camera import handle_camera_command
from friday.Commands.face_auth import handle_face_command, verify_face
from friday.AI.chat import handle_chat, set_session_context

load_dotenv()

state = FridayState()

print("FRIDAY online\n")
# Startup pe face verify karo
from friday.Commands.face_auth import (
    verify_face, log_intruder, get_intruder_report, clear_intruder_log
)

_face_result = verify_face()

if _face_result == "boss":
    print("✅ Boss identified.")
    # Check karo koi intruder tha kya
    intruder_logs = get_intruder_report()
    if intruder_logs:
        count = len(intruder_logs)
        last_time = intruder_logs[-1]["time"]
        speak(
            f"Welcome back boss. "
            f"Heads up — someone accessed your laptop {count} time{'s' if count > 1 else ''} while you were away. "
            f"Last access was at {last_time}."
        )
        print(f"⚠️ Intruder report: {count} access(es)")
        for log in intruder_logs:
            print(f"  - {log['time']}")
        # Log clear karo
        clear_intruder_log()
    else:
        speak("Hey boss, all clear.")

elif _face_result == "unknown":
    speak(
        "Hey, you're not my boss. "
        "I don't take orders from you. "
        "Harsh will know about this."
    )
    log_intruder()
    print("⚠️ Unknown user — logged.")

elif _face_result == "not_registered":
    print("ℹ️ No face registered. Say 'register my face'.")

elif _face_result == "no_face":
    print("ℹ️ No face detected at startup.")


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

    # Standby mein silent listen
    if state.standby:
        user_input = listen(silent=True)
    else:
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
            # Face verify karo
            _current_face = verify_face()

            if _current_face == "boss":

                # Intruder log check karo
                intruder_logs = get_intruder_report()
                if intruder_logs:
                    count = len(intruder_logs)
                    last_time = intruder_logs[-1]["time"]
                    times = ", ".join([l["time"] for l in intruder_logs])
                    
                    # Context set karo taaki AI jaane
                    set_session_context(
                        f"Someone unknown tried to access Friday {count} time(s) "
                        f"while boss was away. Access times: {times}. "
                        f"Friday doesn't know who it was — just that face recognition "
                        f"marked them as unknown. Boss just got back and was informed."
                    )
                    
                    speak(
                        f"Hey boss! Heads up — someone tried to access me "
                        f"{count} time{'s' if count > 1 else ''} while you were away. "
                        f"Last attempt was at {last_time}."
                    )
                    clear_intruder_log()
                else:
                    import random
                    greetings = [
                        "Yeah boss?",
                        "Hey! What's up?",
                        "I'm here, what do you need?",
                        "Listening, boss.",
                        "What's good?",
                    ]
                    speak(random.choice(greetings))
            elif _current_face == "unknown":
                speak("You're not my boss. I don't take orders from you.")
                log_intruder()
            else:
                import random
                greetings = [
                    "Yeah boss?",
                    "Hey! What's up?",
                    "Listening, boss.",
                ]
                speak(random.choice(greetings))

            state.touch()
            continue

    # Active check
    if not state.active:
        continue

    # EXIT
    if user_input.lower().strip() == "exit":
        speak("See you Later, boss.")
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
    
    #Camera Feed 
    if handle_camera_command(user_input):
        state.touch()
        continue

    #face Authentication
    if handle_face_command(user_input):
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
    
    #Git Commands
    if handle_git_command(user_input):
        state.touch()
        continue
    
    #network speed
    if handle_network_command(user_input):
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