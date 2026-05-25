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
    "explain": "Explain what, boss? Say 'explain screen' if you want me to read the screen.",
    "summarize": "Summarize what? Say 'summarize screen' to summarize what's on screen.",
    "summarise": "Summarize what? Say 'summarise screen' to summarize what's on screen.",
    "professional": "Make what professional? Say 'make screen professional' for screen rewrite.",
    "read": "Read what, boss? Say 'read screen' to read what's on screen.",
    "bright": "What do you need, boss?",
    "screen": "What do you want with the screen? Explain, summarise, or make it professional?",
    "solve": "Solve what, boss? Say 'solve screen' for the problem on screen.",
    "answer": "Answer what? Say 'solve screen' for the problem on screen.",
}

SOLVE_TRIGGERS = [
    "solve this", "solve screen", "solve question",
    "answer this", "answer the question",
    "question solve karo", "is question ka answer",
    "solve kar", "solve karo", "solve it",
    "is problem ka solution", "leetcode solve",
]

GUIDE_TRIGGERS = [
    "help me solve", "guide karo", "guide me",
    "help karo", "samjhao", "explain karo question",
    "hint do", "hints do", "kaise solve karu",
    "help solve", "meri help karo",
    "intuition build karo", "sikhao",
    "step by step", "walk me through",
    "approach batao", "approach kya hogi",
]

# Guide session state
_guide_session = {
    "active": False,
    "problem": "",
    "conversation": [],
    "step": 0,
}


def _start_guide_session(screen_text: str):
    """Socratic guide mode start karo."""
    global _guide_session

    _guide_session["active"] = True
    _guide_session["problem"] = screen_text
    _guide_session["step"] = 0
    _guide_session["conversation"] = []

    # Pehle problem analyze karo
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
You are a Socratic programming mentor — like a great teacher, not an answer machine.

Your job: Guide the student to solve the problem THEMSELVES.

FIRST RESPONSE — Do ALL of these:
1. Briefly explain what the problem is asking (1-2 lines)
2. Tell which DSA pattern/concept this belongs to (e.g., "This is a Backtracking problem")
3. Ask WHY this pattern fits — make them think
4. Ask one specific question to check their understanding

RULES:
- NEVER give the solution or code directly
- Ask one question at a time
- Build intuition step by step
- If they're stuck, give a small hint — not the answer
- Celebrate small wins — "Good thinking boss!"
- Keep responses conversational and short
- Speak like a cool senior developer, not a textbook
"""
            },
            {
                "role": "user",
                "content": f"Student needs help with this problem:\n\n{screen_text}\n\nStart the guidance session."
            }
        ],
    )

    reply = response.choices[0].message.content
    _guide_session["conversation"].append({
        "role": "assistant",
        "content": reply
    })

    print("\n🎓 GUIDE MODE:\n", reply)
    speak(_get_speakable(reply))


def _get_speakable(text: str) -> str:
    """Long text ko speakable banao."""
    # Code blocks remove karo
    import re
    text = re.sub(r'```[\s\S]*?```', 'Check the terminal for code, boss.', text)
    # First 2 sentences lo
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
    return '. '.join(sentences[:3]) + '.' if sentences else text


def continue_guide_session(user_input: str) -> bool:
    """
    Guide session continue karo — user ka response process karo.
    Returns True agar guide session active hai.
    """
    global _guide_session

    if not _guide_session["active"]:
        return False

     # Exit command — guide se pehle main loop handle kare
    if user_input.lower().strip() == "exit":
        _guide_session["active"] = False
        return False

    # Session end commands
    if any(t in user_input.lower() for t in [
        "guide band karo", "stop guide", "guide stop",
        "direct answer do", "bas karo", "exit guide",
        "solve kar abhi", "direct solution",
    ]):
        # Direct solve karo
        if "solve" in user_input.lower() or "direct" in user_input.lower():
            speak("Okay boss, giving you the direct solution.")
            _guide_session["active"] = False

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Give complete working solution. Code only with brief comments."
                    },
                    {
                        "role": "user",
                        "content": f"Solve this:\n\n{_guide_session['problem']}"
                    }
                ],
            )
            solution = response.choices[0].message.content
            print("FRIDAY Solution:\n", solution)

            import pyperclip
            import pyautogui
            import time
            pyperclip.copy(solution)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'v')
        else:
            speak("Guide session ended, boss.")
            _guide_session["active"] = False
        return True

    # User ka response process karo
    _guide_session["conversation"].append({
        "role": "user",
        "content": user_input
    })

    # Context build karo
    messages = [
        {
            "role": "system",
            "content": f"""
You are a Socratic programming mentor.

Problem being solved:
{_guide_session['problem']}

RULES:
- NEVER give direct solution or complete code
- Ask one question at a time
- If answer is correct → validate + next hint
- If answer is wrong → gentle correction + nudge
- If stuck → give smallest possible hint
- Build towards solution step by step
- Keep responses SHORT — 3-4 lines max
- End every response with a question
- Celebrate progress — "Nice thinking!", "Exactly boss!"
"""
        }
    ] + _guide_session["conversation"]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
    )

    reply = response.choices[0].message.content
    _guide_session["conversation"].append({
        "role": "assistant",
        "content": reply
    })

    # History limit
    if len(_guide_session["conversation"]) > 20:
        _guide_session["conversation"] = _guide_session["conversation"][-20:]

    print("\n🎓 FRIDAY:\n", reply)
    speak(_get_speakable(reply))
    return True


def handle_screen_command(user_input: str) -> bool:
    """
    Screen command handle karo.
    Returns True agar command handle hua, False otherwise.
    """
    u = user_input.lower().strip()

    # Solo word check — sirf exact single word match
    if u.strip() in SOLO_WORDS and len(u.strip().split()) == 1:
        speak(SOLO_WORDS[u.strip()])
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

    # SOLVE/ANSWER question from screen
    if any(t in u for t in SOLVE_TRIGGERS):
        screen_text = read_screen()
        if not screen_text.strip():
            speak("Screen pe kuch readable nahi mila boss.")
            return True

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an expert programming and problem-solving assistant.

The user has a problem/question on their screen.

RULES:
- Read the problem carefully from the screen text.
- Provide a complete, working solution.
- If it's a coding problem, write clean working code.
- If it's a math problem, solve it step by step.
- If it's a general question, answer it directly.
- Do NOT ask for permission or clarification.
- Just solve it directly.
- Keep explanation brief — focus on the solution.
"""
                },
                {
                    "role": "user",
                    "content": f"Solve this problem from my screen:\n\n{screen_text}"
                }
            ],
        )

        solution = response.choices[0].message.content
        print("FRIDAY Solution:\n", solution)
        speak("Got the solution boss, pasting it for you.")

        # Solution paste karo jahan cursor hai
        import pyperclip
        import pyautogui
        import time
        pyperclip.copy(solution)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')

        return True

    # MODE 1 — Direct Solve
    if any(t in u for t in SOLVE_TRIGGERS):
        screen_text = read_screen()
        if not screen_text.strip():
            speak("Screen pe kuch readable nahi mila boss.")
            return True

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an expert programming assistant.
User wants a DIRECT solution to the problem on screen.

RULES:
- Provide complete working solution immediately.
- Write clean, well-commented code.
- Brief explanation after code — not before.
- No asking for clarification — just solve.
"""
                },
                {
                    "role": "user",
                    "content": f"Solve this completely:\n\n{screen_text}"
                }
            ],
        )

        solution = response.choices[0].message.content
        print("FRIDAY Solution:\n", solution)
        speak("Got the solution boss, pasting it now.")

        import pyperclip
        import pyautogui
        import time
        pyperclip.copy(solution)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        return True

    # MODE 2 — Guide Mode (Socratic)
    if any(t in u for t in GUIDE_TRIGGERS):
        screen_text = read_screen()
        if not screen_text.strip():
            speak("Screen pe kuch readable nahi mila boss.")
            return True

        # Guide session start karo
        _start_guide_session(screen_text)
        return True

    return False


def _get_speakable(text: str) -> str:
    """Text ko speakable banao — code blocks hata, reasonable length rakho."""
    import re

    # Code blocks remove karo
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Markdown remove karo
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    
    # Clean up
    text = text.strip()

    # Agar 400 chars se chhota hai toh poora bolo
    if len(text) <= 400:
        return text

    # Warna pehle 400 chars tak complete sentence dhundho
    truncated = text[:400]
    last_period = max(
        truncated.rfind('.'),
        truncated.rfind('?'),
        truncated.rfind('!')
    )

    if last_period > 200:
        return truncated[:last_period + 1]

    return truncated + "..."