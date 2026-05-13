"""
Screen reading aur OCR-based commands.
"""

import re
import time
import pyautogui
import pyperclip
from mss import mss as MSS
from PIL import Image
import pytesseract
from groq import Groq
import os
from dotenv import load_dotenv

from friday.app_config import USERNAME
pytesseract.pytesseract.tesseract_cmd = (
    rf"C:\Users\{USERNAME}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)

from friday.voice import speak, should_speak
from friday.Personality.prompts import (
    SCREEN_EXPLAIN_PROMPT,
    SCREEN_SUMMARIZE_PROMPT,
    SCREEN_PROFESSIONAL_PROMPT,
)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def read_screen() -> str:
    with MSS() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img = img.convert("L")
        raw_text = pytesseract.image_to_string(img)

        clean_lines = []
        for line in raw_text.split("\n"):
            line = line.strip()

            if len(line) < 8:
                continue

            if re.search(
                r"\b\w+\.(txt|py|pdf|docx|xlsx|jpg|png|mp4|exe|json)\b",
                line,
                re.IGNORECASE,
            ):
                continue

            menu_words = {
                "file", "edit", "view", "insert", "format",
                "tools", "help", "window", "ht", "h1", "bis",
            }
            line_words_lower = set(line.lower().split())
            if len(line_words_lower.intersection(menu_words)) >= 2:
                continue

            if re.search(r"\bLn\b|\bCol\b|\bUTF\b|\bCRLF\b|\bENG\b", line):
                continue

            if "%" in line:
                continue

            if re.search(r"\d+°", line):
                continue

            if any(w in line.lower() for w in ["sunny", "cloudy", "rainy", "windy", "humid"]):
                continue

            if re.search(r"\d{2}-\d{2}-\d{4}", line):
                continue

            symbol_count = sum(1 for c in line if c in "@*#^~`[]{}|\\<>()°©®™$&_+=/")
            if symbol_count > 2:
                continue

            alpha_ratio = sum(c.isalpha() for c in line) / len(line)
            if alpha_ratio < 0.5:
                continue

            if line.lower().startswith("q "):
                continue

            # Consecutive caps filter — allow BCA, MBA etc
            caps_matches = re.findall(r"[A-Z]{3,}", line)
            normal_words = [
                w for w in line.split()
                if w.islower() or (len(w) > 1 and w[0].isupper() and w[1:].islower())
            ]
            if caps_matches and len(normal_words) < 2:
                continue

            # Bracket/paren heavy
            bracket_count = sum(1 for c in line if c in "()[]{}@*#^~`")
            if bracket_count > 2:
                continue

            clean_lines.append(line)

        return "\n".join(clean_lines).strip()


def handle_explain_screen():
    screen_text = read_screen()
    if not screen_text.strip():
        speak("Screen pe kuch readable nahi mila boss.")
        return

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SCREEN_EXPLAIN_PROMPT},
            {"role": "user", "content": screen_text},
        ],
    )
    reply = response.choices[0].message.content
    sentences = [s.strip() for s in reply.replace("\n", " ").split(".") if s.strip()]
    short_reply = ". ".join(sentences[:2]) + "." if sentences else reply
    print("FRIDAY:", short_reply)
    if should_speak(short_reply):
        speak(short_reply)


def handle_summarize_screen():
    screen_text = read_screen()
    if not screen_text.strip():
        speak("Screen pe kuch readable nahi mila boss.")
        return

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SCREEN_SUMMARIZE_PROMPT},
            {"role": "user", "content": f"Summarize this screen content:\n\n{screen_text}"},
        ],
    )
    reply = response.choices[0].message.content
    sentences = [s.strip() for s in reply.replace("\n", " ").split(".") if s.strip()]
    short_reply = ". ".join(sentences[:2]) + "." if sentences else reply
    print("FRIDAY:", short_reply)
    speak(short_reply)


def handle_professional_screen():
    screen_text = read_screen()
    if not screen_text.strip():
        speak("Screen pe kuch readable nahi mila boss.")
        return

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SCREEN_PROFESSIONAL_PROMPT},
            {"role": "user", "content": f"Rewrite this text professionally, every single line:\n\n{screen_text}"},
        ],
    )
    reply = response.choices[0].message.content
    print("FRIDAY:", reply)

    if should_speak(reply):
        sentences = [s.strip() for s in reply.replace("\n", " ").split(".") if s.strip()]
        short_reply = ". ".join(sentences[:2]) + "." if sentences else reply
        speak(short_reply)

    # Notepad mein paste karo
    try:
        import pygetwindow as gw
        notepad_windows = [
            w for w in gw.getAllWindows()
            if "notepad" in w.title.lower() or ".txt" in w.title.lower()
        ]
        if notepad_windows:
            notepad_windows[0].activate()
            time.sleep(0.8)
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.3)
            pyperclip.copy(reply)
            pyautogui.hotkey("ctrl", "v")
            speak("Notepad updated, boss.")
        else:
            pyperclip.copy(reply)
            speak("Copied to clipboard boss, Ctrl V se paste kar lo.")
    except Exception as e:
        print(f"Paste error: {e}")
        pyperclip.copy(reply)
        speak("Copied to clipboard boss.")


# Trigger lists
EXPLAIN_TRIGGERS = [
    "explain screen", "plain screen", "a plane screen",
    "explain the screen", "screen explain", "screen ko explain",
    "bright screen", "screen bright",
    "screen batao", "screen kya hai", "screen dekho",
]

SUMMARIZE_TRIGGERS = [
    "summarize screen", "summarise screen",
    "summarize the screen", "summarise the screen",
    "screen summarize", "screen summarise",
    "screen ko summarize", "screen summary",
]

SOLO_WORDS = {
    "explain": "explain screen bolo boss.",
    "summarize": "summarise screen bolo boss.",
    "summarise": "summarise screen bolo boss.",
    "professional": "make screen professional bolo boss.",
    "read": "read screen bolo boss.",
    "bright": "Kya karna hai boss? Thoda clear karo.",
    "screen": "Kya karna hai screen ke saath boss? Explain, summarise, ya professional?",
}


def handle_screen_command(user_input: str) -> bool:
    """
    Screen command handle karo.
    Returns True agar command handle hua, False otherwise.
    """
    u = user_input.lower().strip()

    # Solo word check
    if u in SOLO_WORDS:
        speak(SOLO_WORDS[u])
        return True

    # Summarize
    if any(t in u for t in SUMMARIZE_TRIGGERS):
        handle_summarize_screen()
        return True

    # Explain
    if any(t in u for t in EXPLAIN_TRIGGERS):
        handle_explain_screen()
        return True

    # Professional
    if "professional" in u and "screen" in u:
        handle_professional_screen()
        return True

    # Read screen
    if "read screen" in u or "screen padho" in u:
        screen_text = read_screen()
        print("CLEAN SCREEN:\n", screen_text)
        speak("I've read the screen, sir.")
        return True

    return False