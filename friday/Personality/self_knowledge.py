"""
Friday khud apna code padhti hai aur self-knowledge generate karti hai.
"""

import os


def _read_file_summary(filepath: str) -> str:
    """File ka detailed summary banao — functions + docstrings + key logic."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        summary_parts = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Function definitions
            if line.startswith("def "):
                func_name = line.split("(")[0].replace("def ", "")
                func_sig = line

                # Docstring dhundho
                docstring = ""
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        j = i + 1
                        doc_lines = []
                        while j < len(lines):
                            doc_lines.append(lines[j].strip())
                            if j > i + 1 and (
                                '"""' in lines[j] or "'''" in lines[j]
                            ):
                                break
                            j += 1
                        docstring = " ".join(doc_lines).replace('"""', "").replace("'''", "").strip()

                summary_parts.append(
                    f"  fn:{func_name} — {docstring[:120] if docstring else 'no description'}"
                )

            # Key variable assignments — important config
            elif any(kw in line for kw in [
                "TRIGGERS", "triggers", "MODEL =", "VOICE =",
                "MAX_HISTORY", "THRESHOLD", "SCORE",
            ]):
                if "=" in line and not line.startswith("#"):
                    summary_parts.append(f"  config: {line[:100]}")

            i += 1

        return "\n".join(summary_parts[:30])  # Max 30 lines per file

    except Exception as e:
        return f"  (could not read: {e})"


def get_module_summary() -> str:
    """
    Friday ke saare modules ka detailed summary banao.
    Actual implementation details include karo.
    """
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    modules = {
        "friday/Automation/volume.py": """
Volume control uses PowerShell COM injection to control Windows audio.
Injects a C# class implementing IAudioEndpointVolume COM interface.
Functions: get_volume() returns 0-100 int, set_volume(level) sets exact level,
volume_up(amount=10) increases by amount, volume_down(amount=10) decreases,
mute() and unmute() toggle mute state.
Commands: 'volume up', 'volume down', 'mute', 'unmute', 'volume 50 karo', 'volume kitna hai'
""",
        "friday/memory.py": """
Two-layer memory system stored in memory.json file.
Layer 1 - Personal facts: Groq LLM extracts key-value pairs from conversation
(name, age, city, preferences etc) and saves them permanently.
Layer 2 - Conversation history: Last 20 conversation turns saved with timestamps.
Both layers injected into chat system prompt so Friday always has context.
Functions: extract_and_save() uses LLM to identify personal facts,
get_memory() loads all saved data, should_check_memory() decides if input has personal info.
""",
        "friday/AI/intent.py": """
Natural language intent detection using Groq llama-3.1-8b-instant model.
Sends user input to LLM with INTENT_PROMPT containing 30+ example mappings.
LLM returns JSON: {"action": "open/close_tab/search/none", "target": "instagram"}.
Actions handled: open, close_tab, close_window, close_all_tabs, close_all_apps,
search, make_professional, solve_screen, guide_screen, get_time, get_date.
JSON parsing is defensive — malformed responses return False to fall to chat.
""",
        "friday/AI/chat.py": """
Conversational AI using Groq llama-3.3-70b-versatile model.
Maintains conversation history (MAX_HISTORY=10 turns) in memory list.
System prompt includes: personality rules, memory data, conversation history,
self-knowledge about codebase, language rules (English default).
Temperature 0.7 for natural responses, max 200 tokens for conciseness.
Session context can be set for special situations (like intruder reports).
""",
        "friday/Commands/screen.py": """
OCR-based screen reading using pytesseract + mss for screen capture.
read_screen() captures full screen, converts to grayscale, runs OCR,
then filters noise (taskbar, UI elements, symbols, short lines).
Three modes: explain (2 sentence description), summarize (brief summary),
professional (rewrites content in formal tone, pastes to notepad or clipboard).
Guide mode: Socratic LeetCode tutoring — never gives direct answer, asks questions.
Solve mode: Reads problem from screen, generates complete solution, pastes it.
Code review: Takes screenshot, sends to Groq Vision for detailed review.
""",
        "friday/Commands/notes.py": """
Smart notes system with time-aware reminders stored in friday_notes.json.
add_note() extracts time from content using regex (4 baje, 30 minutes mein etc).
If time found, launches separate Python subprocess (_reminder_process.py)
that waits until target time then fires: Tkinter popup + winsound beep + gTTS voice.
Reminders survive Friday restart — restore_reminders() called at startup.
restore_reminders() reads notes file, finds pending reminders, relaunches subprocesses.
""",
        "friday/Automation/apps.py": """
App management using psutil for process control and os.startfile for launching.
open_app() checks: WEB_APPS dict, SYSTEM_APPS dict, APP_FIRST dict, file search.
close_all_apps() builds protected PID set: Friday's own PID + parent chain + children.
Protected names list prevents killing system processes (explorer, svchost etc).
close_specific_apps() keeps user-specified apps, kills rest.
Uses APP_ALIASES dict to map friendly names to process names (calculator → calc.exe).
""",
        "friday/Commands/spotify.py": """
YouTube Music control using yt-dlp for search and browser for playback.
play_song() calls yt-dlp with 'ytsearch1:query --get-id' to find video ID.
Opens youtube.com/watch?v=ID in browser for autoplay — no Spotify Premium needed.
Playback controls use pygetwindow to find and focus Chrome/YouTube window,
then sends keyboard shortcuts: k=pause, Shift+N=next, Shift+P=previous.
""",
        "friday/voice.py": """
TTS: Piper Amy (en_US-amy-medium.onnx) — completely offline, no API needed.
speak() loads model once, synthesizes WAV to temp file, plays via sounddevice.
Interrupt support: _speaking flag + _interrupt_flag + sd.stop() for mid-speech stop.
Background thread monitors mic during speech for interrupt words (stop, friday, ruko).
STT: Google Speech Recognition with 5s timeout, 10s phrase limit.
Mic lock (_mic_lock threading.Lock) prevents concurrent microphone access.
""",
        "friday/Commands/search.py": """
Real-time web search using DuckDuckGo (ddgs library) — no API key needed.
For news queries: uses ddgs.news() for structured news articles.
For general queries: uses ddgs.text() for web results.
Results passed to Groq LLM to synthesize natural 2-3 sentence spoken answer.
Runs in background thread so Friday doesn't block while searching.
News triggers: 'latest news', 'news batao', 'kya chal raha hai' etc.
""",
        "friday/Commands/face_auth.py": """
Face recognition using MediaPipe FaceMesh — 478 facial landmarks in 3D.
register_face() captures 5 frames, extracts landmarks, saves average vector as JSON.
verify_face() captures frame, extracts landmarks, computes cosine similarity.
Threshold 0.97 — high enough to reject impostors, reliable for boss recognition.
Intruder logging: unknown users logged with timestamp in friday_intruder_log.json.
Boss return: checks intruder log, reports how many times someone accessed, clears log.
""",
    }

    summary_lines = [
        "FRIDAY's actual implementation details — how each module works:\n"
    ]

    for rel_path, description in modules.items():
        full_path = os.path.join(base, rel_path.replace("/", os.sep))
        summary_lines.append(f"[{rel_path}]")
        summary_lines.append(description.strip())
        summary_lines.append("")

    return "\n".join(summary_lines)


def get_recent_changes() -> str:
    """Recent feature additions from memory."""
    import json
    try:
        with open("memory.json", "r") as f:
            memory = json.load(f)
        changes = memory.get("__friday_features__", [])
        if changes:
            return "Recent additions by Harsh:\n" + "\n".join(
                f"- {c}" for c in changes
            )
    except:
        pass
    return ""


def log_new_feature(feature: str):
    """New feature log karo."""
    import json
    from datetime import datetime

    try:
        with open("memory.json", "r") as f:
            memory = json.load(f)
    except:
        memory = {}

    features = memory.get("__friday_features__", [])
    entry = f"{feature} (added {datetime.now().strftime('%d %b %Y')})"
    if entry not in features:
        features.append(entry)
    memory["__friday_features__"] = features[-10:]

    with open("memory.json", "w") as f:
        json.dump(memory, f, indent=4)