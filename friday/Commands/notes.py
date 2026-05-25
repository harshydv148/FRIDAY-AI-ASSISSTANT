"""
Quick Notes with Smart Reminders — note taking + auto recall.
"""
import os
import json
import re
import threading
import time
import subprocess  # yeh add karo
from datetime import datetime, timedelta
from friday.voice import speak


NOTES_FILE = "friday_notes.json"


def load_notes() -> list:
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_notes(notes: list):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=4, ensure_ascii=False)


def _parse_time_from_note(content: str):
    content_lower = content.lower()
    now = datetime.now()

    # PEHLE relative time check karo — "X minute mein", "X hour mein"
    # Yeh specific match hai — "1 minut mein", "30 minutes baad"
    relative_match = re.search(
        r'(\d+)\s*(?:minute|minutes|min|mins|minut|minuts|second|sec|secs|hour|hr|ghanta|ghante)'
        r'\s*(?:mein|baad|me|bad|ke baad)?',
        content_lower
    )

    if relative_match:
        full_match = relative_match.group(0).lower()
        amount = int(relative_match.group(1))

        if any(w in full_match for w in ["hour", "hr", "ghanta", "ghante"]):
            return now + timedelta(seconds=amount * 3600)
        elif any(w in full_match for w in ["second", "sec"]):
            return now + timedelta(seconds=amount)
        else:  # minutes
            return now + timedelta(seconds=amount * 60)

    # Specific time — "4 baje", "4 pm", "4:30"
    time_match = re.search(
        r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|baje|bajke|baj ke)',
        content_lower
    )

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        meridiem = time_match.group(3)

        if meridiem == "pm" and hour != 12:
            hour += 12
        elif meridiem == "am" and hour == 12:
            hour = 0

        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    # Kal
    if "kal" in content_lower:
        return now.replace(hour=9, minute=0) + timedelta(days=1)

    return None


def _fire_reminder(note_content: str, remind_at: datetime):
    """Alag process mein reminder chalao — Friday se independent."""
    import sys

    safe_content = note_content.replace('"', "'").replace('\n', ' ')

    script = f"""
import time
from datetime import datetime

target = datetime.strptime("{remind_at.strftime('%Y-%m-%d %H:%M:%S')}", "%Y-%m-%d %H:%M:%S")
now = datetime.now()
wait = (target - now).total_seconds()

if wait > 0:
    time.sleep(wait)

# Beep sound pehle
try:
    import winsound
    for _ in range(5):
        winsound.Beep(1000, 400)
        time.sleep(0.2)
except Exception as e:
    print(f"Beep error: {{e}}")

# Windows popup
# Custom popup window
try:
    import tkinter as tk
    from tkinter import font as tkfont

    root = tk.Tk()
    root.title("FRIDAY Reminder")
    root.geometry("450x200")
    root.attributes("-topmost", True)
    root.configure(bg="#0b0b0b")
    root.resizable(False, False)

    # Bell icon + title
    title_label = tk.Label(
        root,
        text="REMINDER",
        font=("Consolas", 14, "bold"),
        fg="#00d4ff",
        bg="#0b0b0b"
    )
    title_label.pack(pady=(20, 5))

    # Content
    content_label = tk.Label(
        root,
        text="{safe_content}",
        font=("Consolas", 13),
        fg="#ffffff",
        bg="#0b0b0b",
        wraplength=400,
        justify="center"
    )
    content_label.pack(pady=10, padx=20)

    # Dismiss button
    btn = tk.Button(
        root,
        text="Dismiss",
        font=("Consolas", 11),
        fg="#0b0b0b",
        bg="#00d4ff",
        relief="flat",
        padx=20,
        pady=5,
        command=root.destroy
    )
    btn.pack(pady=15)

    root.mainloop()

except Exception as e:
    print(f"Popup error: {{e}}")

# Voice reminder
try:
    import pygame
    from gtts import gTTS
    import os
    import uuid

    pygame.mixer.init()
    tts = gTTS(text="Boss, reminder. {safe_content}", lang="en")
    filename = f"rem_{{uuid.uuid4().hex[:6]}}.mp3"
    tts.save(filename)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()
    os.remove(filename)
except Exception as e:
    print(f"Voice error: {{e}}")
"""

    script_path = os.path.join(
        os.path.dirname(__file__), "_reminder_process.py"
    )
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    try:
        subprocess.Popen(
            [sys.executable, script_path],
            #stdout=subprocess.DEVNULL,
            #stderr=subprocess.DEVNULL,
        )
        print(f"🔔 Reminder process started: {note_content}")
    except Exception as e:
        print(f"Reminder process error: {e}")


def _reminder_thread(note_content: str, remind_at: datetime):
    """Thread wrapper — _fire_reminder ko call karo."""
    now = datetime.now()
    wait_seconds = (remind_at - now).total_seconds()
    if wait_seconds <= 0:
        return
    print(f"⏰ Reminder set for {remind_at.strftime('%I:%M %p')} — {note_content}")
    _fire_reminder(note_content, remind_at)
    

def add_note(content: str, silent: bool = False):
    remind_at = _parse_time_from_note(content)
    print(f"🔍 Note: '{content}' | Remind at: {remind_at}")
    """Note add karo aur agar time hai toh reminder set karo."""
    notes = load_notes()

    # Time extract karo
    remind_at = _parse_time_from_note(content)
    remind_str = remind_at.strftime("%d %b %Y %I:%M %p") if remind_at else None

    entry = {
        "id": len(notes) + 1,
        "content": content,
        "time": datetime.now().strftime("%d %b %Y %H:%M"),
        "remind_at": remind_str,
        "reminded": False,
    }

    notes.append(entry)
    save_notes(notes)
    print(f"📝 Note saved: {content}")

    if remind_at:
        # Reminder thread start karo
        thread = threading.Thread(
            target=_fire_reminder,
            args=(content, remind_at),
            daemon=True
        )
        thread.start()
        if not silent:
            time_str = remind_at.strftime("%I:%M %p")
            speak(f"Noted boss, I'll remind you at {time_str}.")
    else:
        if not silent:
            speak("Got it boss, noted.")


def restore_reminders():
    """
    App restart hone pe pending reminders restore karo.
    Session start pe call karo.
    """
    notes = load_notes()
    now = datetime.now()
    restored = 0

    for note in notes:
        if note.get("remind_at") and not note.get("reminded"):
            try:
                remind_at = datetime.strptime(
                    note["remind_at"], "%d %b %Y %I:%M %p"
                )
                if remind_at > now:
                    thread = threading.Thread(
                        target=_fire_reminder,
                        args=(note["content"], remind_at),
                        daemon=True
                    )
                    thread.start()
                    restored += 1
            except:
                continue

    if restored > 0:
        print(f"🔔 Restored {restored} pending reminder(s).")


def show_notes(count: int = 5):
    """Last N notes batao."""
    notes = load_notes()
    if not notes:
        speak("No notes yet, boss.")
        return

    recent = notes[-count:]
    print("\n📝 Your Notes:")
    for note in recent:
        reminder_info = f" [Remind: {note['remind_at']}]" if note.get("remind_at") else ""
        print(f"  [{note['time']}] {note['content']}{reminder_info}")

    if len(recent) == 1:
        speak(f"Your last note — {recent[-1]['content']}")
    else:
        speak(f"You have {len(notes)} notes boss. Last — {recent[-1]['content']}")


def delete_last_note():
    notes = load_notes()
    if not notes:
        speak("No notes to delete, boss.")
        return
    deleted = notes.pop()
    save_notes(notes)
    print(f"🗑️ Deleted: {deleted['content']}")
    speak("Deleted your last note, boss.")


def clear_all_notes():
    save_notes([])
    speak("All notes cleared, boss.")
    print("🗑️ All notes cleared.")


def show_pending_reminders():
    """Pending reminders dikhao."""
    notes = load_notes()
    now = datetime.now()
    pending = []

    for note in notes:
        if note.get("remind_at") and not note.get("reminded"):
            try:
                remind_at = datetime.strptime(
                    note["remind_at"], "%d %b %Y %I:%M %p"
                )
                if remind_at > now:
                    pending.append((note["content"], remind_at))
            except:
                continue

    if not pending:
        speak("No pending reminders, boss.")
        return

    print(f"\n🔔 Pending Reminders ({len(pending)}):")
    for content, remind_at in pending:
        print(f"  [{remind_at.strftime('%I:%M %p')}] {content}")

    speak(f"You have {len(pending)} pending reminder{'s' if len(pending) > 1 else ''}, boss.")


def handle_notes_command(user_input: str) -> bool:
    u = user_input.lower()

    # Show pending reminders
    if any(t in u for t in [
        "pending reminders", "reminders dikhao",
        "kya reminders hain", "reminders kya hain",
    ]):
        show_pending_reminders()
        return True

    # Show notes
    if any(t in u for t in [
        "show notes", "read notes", "notes dikhao",
        "meri notes", "notes kya hain", "notes batao",
        "last note", "my notes",
    ]):
        show_notes()
        return True

    # Delete last note
    if any(t in u for t in [
        "delete last note", "last note delete",
        "note delete karo", "pichli note hatao",
    ]):
        delete_last_note()
        return True

    # Clear all
    if any(t in u for t in [
        "clear notes", "clear all notes",
        "saari notes delete", "notes clear karo",
        "all notes delete", "notes delete",
        "delete all notes", "remove all notes",
    ]):
        clear_all_notes()
        return True

    # Add note
    NOTE_TRIGGERS = [
        "note karo", "note kar", "note down",
        "save note", "add note", "note likh",
        "note it", "note:", "remind me",
        "remind karna", "yaad dilana",
        "alert karna", "alert karo", "alert lagao",
        "remind karo", "yaad rakhna",
        "baje remind", "baje alert", "baje batana",
    ]

    # Direct time trigger — "X minute mein Y" ya "X baje Y"
    TIME_DIRECT = [
        "minute mein", "minutes mein", "minut mein",
        "hour mein", "ghante mein", "ghanta mein",
        "second mein", "sec mein",
        "baje", "bajke", "baj ke",
        "kal tak", "kal ko",
    ]

    # Check karo — koi note trigger hai?
    has_note_trigger = any(t in u for t in NOTE_TRIGGERS)

    # Check karo — direct time phrase hai?
    has_time = any(t in u for t in TIME_DIRECT)

    if has_note_trigger or has_time:
        content = u
        # Saare triggers remove karo
        for t in NOTE_TRIGGERS:
            content = content.replace(t, "").strip()
        content = content.replace("friday", "").strip()
        # Agar content sirf time hai toh original user_input use karo
        if not content or len(content) < 3:
            content = u  # original rakho taaki reminder fire ho

        if content:
            add_note(content)
        else:
            speak("Kya note karun boss?")
        return True

    return False