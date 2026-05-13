"""
File operations — find, open, type commands.
"""

import os
import time
import pyautogui
import pyperclip
from groq import Groq
from dotenv import load_dotenv

from friday.voice import speak
from friday.Personality.prompts import TYPE_PROMPT

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def find_app(app_name: str) -> str | None:
    start_menu_paths = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        rf"C:\Users\{os.getlogin()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
    ]
    valid_extensions = (".lnk", ".exe")

    for path in start_menu_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if app_name.lower() in file.lower() and file.endswith(valid_extensions):
                    return os.path.join(root, file)
    return None


# Yeh folders skip karo — system/dev folders hain
SKIP_DIRS = {
    ".venv", "venv", "env", "__pycache__", "node_modules",
    ".git", "site-packages", ".env", "dist", "build",
    ".idea", ".vscode",
}

# Yeh extensions skip karo — system files hain
SKIP_EXTENSIONS = {
    ".pyd", ".dll", ".sys", ".exe", ".bin", ".dat",
    ".pyc", ".pyo", ".so", ".lib", ".obj", ".cache",
}

def find_file(file_name: str) -> str | None:
    # Bohot chote ya generic words ke liye search mat karo
    if len(file_name) < 3:
        speak("Thoda specific naam bolo boss.")
        return None

    search_paths = [
        f"C:/Users/{os.getlogin()}/Desktop",
        f"C:/Users/{os.getlogin()}/Downloads",
        f"C:/Users/{os.getlogin()}/Documents",
    ]

    for path in search_paths:
        for root, dirs, files in os.walk(path):
            # Skip unwanted directories
            dirs[:] = [
                d for d in dirs
                if d.lower() not in SKIP_DIRS
                and not d.startswith(".")
            ]

            for file in files:
                # Skip unwanted extensions
                _, ext = os.path.splitext(file)
                if ext.lower() in SKIP_EXTENSIONS:
                    continue

                if file_name.lower() in file.lower():
                    return os.path.join(root, file)
    return None


def find_file_in_folder(folder_name: str, file_name: str) -> str | None:
    base_path = f"C:/Users/{os.getlogin()}/Desktop"
    for root, dirs, files in os.walk(base_path):
        # Skip unwanted directories
        dirs[:] = [
            d for d in dirs
            if d.lower() not in SKIP_DIRS
            and not d.startswith(".")
        ]

        if folder_name.lower() in root.lower():
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in SKIP_EXTENSIONS:
                    continue
                if file_name.lower() in file.lower():
                    return os.path.join(root, file)
    return None

def paste_text(text: str):
    pyperclip.copy(text)
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "v")


def handle_type_command(user_input: str) -> bool:
    """
    'type X' command handle karo — AI se content generate karke paste karo.
    Returns True agar handle hua.
    """
    if not user_input.lower().startswith("type "):
        return False

    type_request = user_input[5:].strip()
    if not type_request:
        speak("Kya type karna hai boss?")
        return True

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": TYPE_PROMPT},
            {"role": "user", "content": f"Type this for me: {type_request}"},
        ],
    )

    generated_text = response.choices[0].message.content
    print("FRIDAY (typing):", generated_text[:100], "...")
    speak(f"Typing {type_request} for you, boss.")
    time.sleep(1)
    paste_text(generated_text)
    return True