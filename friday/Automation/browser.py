"""
Browser control — tabs open/close karna.
"""

import subprocess
import pyautogui
from friday.voice import speak


def close_all_tabs():
    """Chrome gracefully close karo"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True,
            text=True,
        )
        if "chrome.exe" not in result.stdout.lower():
            speak("Chrome is not running, boss.")
            return

        subprocess.run(
            [
                "powershell",
                "-command",
                "$wshell = New-Object -ComObject wscript.shell; "
                "Get-Process chrome | ForEach-Object { $_.CloseMainWindow() }",
            ],
            capture_output=True,
            timeout=5,
        )
        speak("Chrome closed, boss.")

    except Exception as e:
        print("Chrome close error:", e)
        speak("Couldn't close Chrome, boss.")


def close_current_tab():
    """Active tab band karo — Ctrl+W"""
    try:
        pyautogui.hotkey("ctrl", "w")
        speak("Tab closed, boss.")
    except Exception as e:
        print("Tab close error:", e)


def close_current_window():
    """Active window band karo — Alt+F4"""
    try:
        pyautogui.hotkey("alt", "f4")
        speak("Window closed, boss.")
    except Exception as e:
        print("Window close error:", e)


def handle_close_tabs(user_input: str) -> bool:
    """
    Close tab commands handle karo.
    Returns True agar handle hua.
    """
    u = user_input.lower()

    if "close all tab" in u or "close all chrome" in u:
        has_except = any(
            w in u for w in ["except", "accept", "but not", "keep"]
        )

        if has_except:
            for splitter in ["except", "accept", "but not", "keep"]:
                if splitter in u:
                    except_part = u.split(splitter)[-1].strip()
                    break

            if "firefox" in except_part:
                speak("Closing Chrome, keeping Firefox, boss.")
                close_all_tabs()
            elif "chrome" in except_part:
                speak("Chrome is the only browser I manage tabs for, boss.")
            else:
                close_all_tabs()
        else:
            close_all_tabs()

        return True

    return False