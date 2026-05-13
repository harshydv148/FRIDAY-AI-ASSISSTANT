"""
System commands — shutdown, restart, volume control.
"""

import os
from friday.voice import speak


def handle_system_command(user_input: str) -> bool:
    """
    System commands handle karo.
    Returns True agar handle hua.
    """
    u = user_input.lower()

    if "shutdown" in u:
        speak("Shutting down the system, boss.")
        os.system("shutdown /s /t 5")
        return True

    if "restart system" in u:
        speak("Restarting the system, boss.")
        os.system("shutdown /r /t 5")
        return True

    return False