"""
Screenshot — screen capture karna.
"""

import os
import time
import pyautogui
from datetime import datetime
from friday.voice import speak


def take_screenshot(save_path: str = None) -> str:
    """
    Screenshot lo aur save karo.
    Returns saved file path.
    """
    if not save_path:
        # Default — Desktop pe save karo
        desktop = os.path.expanduser("~\\Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(desktop, f"screenshot_{timestamp}.png")

    time.sleep(0.5)  # thoda wait karo taaki Friday ki window na aaye
    screenshot = pyautogui.screenshot()
    screenshot.save(save_path)
    return save_path


def handle_screenshot_command(user_input: str) -> bool:
    """
    Screenshot commands handle karo.
    Returns True agar handle hua.
    """
    u = user_input.lower()

    screenshot_triggers = [
        "screenshot", "screen shot", "screenshot lo",
        "screenshot le", "capture screen", "screen capture",
        "screen ko capture karo", "photo lo screen ki",
    ]

    if not any(t in u for t in screenshot_triggers):
        return False

    try:
        # Specific folder mein save karna hai?
        if "downloads" in u:
            folder = os.path.expanduser("~\\Downloads")
        elif "documents" in u:
            folder = os.path.expanduser("~\\Documents")
        else:
            folder = os.path.expanduser("~\\Desktop")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(folder, f"screenshot_{timestamp}.png")

        speak("Taking screenshot in 3 seconds, boss.")
        time.sleep(3)  # user ko time do window arrange karne ka

        path = take_screenshot(save_path)
        print(f"📸 Screenshot saved: {path}")
        speak(f"Screenshot saved to {os.path.basename(os.path.dirname(path))}, boss.")
        
        # Screenshot open karo
        os.startfile(path)

    except Exception as e:
        print(f"Screenshot error: {e}")
        speak("Couldn't take screenshot, boss.")

    return True