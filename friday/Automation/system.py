"""
System commands — shutdown, restart, volume control.
"""

import os
from friday.voice import speak


def handle_system_command(user_input: str) -> bool:
    u = user_input.lower()

    if "shutdown" in u:
        speak("Shutting down the system, boss.")
        os.system("shutdown /s /t 5")
        return True

    if "restart system" in u:
        speak("Restarting the system, boss.")
        os.system("shutdown /r /t 5")
        return True

    if any(t in u for t in [
        "lock screen", "lock karo", "lock kar do",
        "screen lock", "lock pc", "lock computer",
        "lock", "pc lock karo"
    ]):
        speak("Locking the screen, boss.")
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return True

    if any(t in u for t in [
        "log out", "logout", "log off",
        "sign out", "log out karo"
    ]):
        speak("Logging out, boss.")
        os.system("shutdown /l")
        return True

    return False