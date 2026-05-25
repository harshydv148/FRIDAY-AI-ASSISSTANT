"""
Timer, Stopwatch, and Alarm — time management.
"""

import time
import threading
import re
from datetime import datetime, timedelta
from friday.voice import speak


# Active timers track karo
active_timers = {}
stopwatch_start = None
stopwatch_running = False


def _timer_thread(seconds: int, label: str):
    """Background mein timer chalaao."""
    time.sleep(seconds)

    # Beep sound
    try:
        import winsound
        for _ in range(3):
            winsound.Beep(1000, 400)
            time.sleep(0.2)
    except Exception as e:
        print(f"Beep error: {e}")

    speak(f"Boss, {label} is done!")
    print(f"⏰ Timer done: {label}")

    if label in active_timers:
        del active_timers[label] 


def start_timer(seconds: int, label: str = "timer"):
    """Timer start karo."""
    if label in active_timers:
        speak(f"{label} already running boss.")
        return

    thread = threading.Thread(
        target=_timer_thread,
        args=(seconds, label),
        daemon=True
    )
    thread.start()
    active_timers[label] = thread

    # Human readable time
    if seconds >= 3600:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        time_str = f"{h} hour{'s' if h > 1 else ''}"
        if m:
            time_str += f" {m} minute{'s' if m > 1 else ''}"
    elif seconds >= 60:
        m = seconds // 60
        s = seconds % 60
        time_str = f"{m} minute{'s' if m > 1 else ''}"
        if s:
            time_str += f" {s} second{'s' if s > 1 else ''}"
    else:
        time_str = f"{seconds} second{'s' if seconds > 1 else ''}"

    speak(f"Timer set for {time_str}, boss.")
    print(f"⏱️ Timer started: {time_str}")


def start_stopwatch():
    global stopwatch_start, stopwatch_running

    if stopwatch_running:
        speak("Stopwatch is already running, boss.")
        return

    stopwatch_running = True
    speak("Stopwatch started, boss.")
    # Thoda wait karo window open hone ka
    time.sleep(0.5)
    stopwatch_start = time.time()
    print("⏱️ Stopwatch started.")

    # Tkinter main thread mein chahiye
    # Isliye subprocess se alag process mein chalao
    import subprocess
    import sys
    import os

    # Temporary script banao
    script = """
import tkinter as tk
import time
import sys

start_time = time.time()  # window open hote hi timer start

root = tk.Tk()
root.title("Stopwatch")
root.geometry("400x200")
root.attributes("-topmost", True)
root.configure(bg="#0b0b0b")
root.resizable(False, False)

time_label = tk.Label(
    root,
    text="00:00:00",
    font=("Consolas", 42, "bold"),
    fg="#00d4ff",
    bg="#0b0b0b"
)
time_label.pack(expand=True, pady=20)

status_label = tk.Label(
    root,
    text="RUNNING",
    font=("Consolas", 10),
    fg="#00ff88",
    bg="#0b0b0b"
)
status_label.pack()

def update():
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    time_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    root.after(100, update)

root.protocol("WM_DELETE_WINDOW", root.destroy)
update()
root.mainloop()
"""

    # Script file save karo
    script_path = os.path.join(os.path.dirname(__file__), "_stopwatch_ui.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    # Alag process mein chalao
    subprocess.Popen(
        [sys.executable, script_path],
        creationflags=subprocess.CREATE_NO_WINDOW
        if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
    )


def _show_stopwatch_window():
    """Tkinter se floating stopwatch window."""
    import tkinter as tk

    root = tk.Tk()
    root.title("⏱️ Stopwatch")
    root.geometry("400x200")
    root.attributes("-topmost", True)  # hamesha upar rahe
    root.configure(bg="#0b0b0b")
    root.resizable(False, False)

    # Remove title bar for clean look
    # root.overrideredirect(True)  # uncomment for borderless

    time_label = tk.Label(
        root,
        text="00:00:00",
        font=("Consolas", 42, "bold"),
        fg="#00d4ff",
        bg="#0b0b0b"
    )
    time_label.pack(expand=True)

    status_label = tk.Label(
        root,
        text="● RUNNING",
        font=("Consolas", 10),
        fg="#00ff88",
        bg="#0b0b0b"
    )
    status_label.pack()

    def update():
        global stopwatch_running
        if not stopwatch_running:
            status_label.config(text="■ STOPPED", fg="#ff4444")
            return

        elapsed = time.time() - stopwatch_start
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        time_label.config(
            text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        root.after(100, update)  # har 100ms update karo

    def on_close():
        global stopwatch_running
        stopwatch_running = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    update()
    root.mainloop()

def stop_stopwatch():
    global stopwatch_start, stopwatch_running
    if not stopwatch_running:
        speak("Stopwatch isn't running, boss.")
        return

    elapsed = time.time() - stopwatch_start
    stopwatch_running = False
    stopwatch_start = None

    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    if minutes > 0:
        time_str = f"{minutes} minutes and {seconds} seconds"
    else:
        time_str = f"{seconds} seconds"

    speak(f"Stopwatch stopped. {time_str}, boss.")
    print(f"⏱️ Elapsed: {time_str}")

    # Window close karo — script file delete karo
    import os
    import subprocess
    import sys

    # Stopwatch process kill karo
    try:
        script_path = os.path.join(
            os.path.dirname(__file__), "_stopwatch_ui.py"
        )
        # Python process dhundho jo is script ko chal raha hai
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline') or []
                if any('_stopwatch_ui.py' in str(c) for c in cmdline):
                    proc.kill()
                    print("🛑 Stopwatch window closed.")
                    break
            except:
                continue
    except Exception as e:
        print(f"Window close error: {e}")


def check_stopwatch():
    """Current stopwatch time check karo."""
    global stopwatch_start, stopwatch_running
    if not stopwatch_running:
        speak("Stopwatch isn't running, boss.")
        return
    elapsed = time.time() - stopwatch_start
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    if minutes > 0:
        speak(f"{minutes} minutes {seconds} seconds so far, boss.")
    else:
        speak(f"{seconds} seconds so far, boss.")


def _alarm_thread(target_time: datetime, label: str):
    """Background mein alarm chalaao."""
    now = datetime.now()
    wait_seconds = (target_time - now).total_seconds()
    if wait_seconds < 0:
        # Kal ke liye set karo
        wait_seconds += 86400
    time.sleep(wait_seconds)
    speak(f"Boss, wake up! {label}")
    print(f"⏰ Alarm: {label}")


def set_alarm(hour: int, minute: int, label: str = "Alarm"):
    """Alarm set karo specific time pe."""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target <= now:
        target += timedelta(days=1)

    thread = threading.Thread(
        target=_alarm_thread,
        args=(target, label),
        daemon=True
    )
    thread.start()

    time_str = target.strftime("%I:%M %p")
    speak(f"Alarm set for {time_str}, boss.")
    print(f"⏰ Alarm set: {time_str}")


def parse_time_to_seconds(text: str) -> int:
    """
    Text se seconds extract karo.
    "10 minutes", "1 hour 30 minutes", "45 seconds" etc.
    """
    total = 0

    # Hours
    h_match = re.search(r'(\d+)\s*(?:hour|hr|ghanta|ghante)', text)
    if h_match:
        total += int(h_match.group(1)) * 3600

    # Minutes
    m_match = re.search(r'(\d+)\s*(?:minute|min|mins|minutes|मिनट)', text)
    if m_match:
        total += int(m_match.group(1)) * 60

    # Seconds
    s_match = re.search(r'(\d+)\s*(?:second|sec|secs|seconds)', text)
    if s_match:
        total += int(s_match.group(1))

    return total


def handle_timer_command(user_input: str) -> bool:
    """
    Timer/Alarm/Stopwatch commands handle karo.
    Returns True agar handle hua.
    """
    # print(f"🔍 TIMER CHECK: '{user_input}'")  # debug
    u = user_input.lower()
    u = user_input.lower()

    # STOPWATCH
    # Agar stopwatch chal rahi hai aur user ne "band karo" ya "rok" bola
    if stopwatch_running and any(t in u for t in [
        "band karo", "band", "rok", "stop", "pause", "ruko"
    ]):
        # But "stopwatch start" ka "start" ignore karo
        if not any(t in u for t in ["start", "chalu", "shuru"]):
            stop_stopwatch()
            return True

    # STOPWATCH — pehle check karo
    stopwatch_words = ["stopwatch", "stop watch", "stopewatch", "stopwach"]
    is_stopwatch = any(t in u for t in stopwatch_words)

    if is_stopwatch:
        # Pehle start check karo
        if any(t in u for t in ["start", "chalu", "shuru", "on", "chalao", "karo"]):
            start_stopwatch()
            return True
        # Phir stop check karo — strict match
        elif any(t in u for t in ["band", "rok", "pause", "end"]) or u.strip() in ["stop stopwatch", "stopwatch stop", "stopwatch band"]:
            stop_stopwatch()
            return True
        elif any(t in u for t in ["check", "kitna", "how long", "time"]):
            check_stopwatch()
            return True
        else:
            start_stopwatch()
            return True
    # ALARM
    alarm_match = re.search(
        r'alarm\s+(?:set\s+)?(?:karo\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
        u
    )
    if alarm_match or "alarm" in u:
        if alarm_match:
            hour = int(alarm_match.group(1))
            minute = int(alarm_match.group(2)) if alarm_match.group(2) else 0
            ampm = alarm_match.group(3)

            if ampm == "pm" and hour != 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0

            set_alarm(hour, minute)
            return True
        else:
            speak("Konse time pe alarm set karun boss? Bolo jaise '7 baje ka alarm'.")
            return True

    # TIMER
    timer_triggers = [
        "timer", "set timer", "timer lagao",
        "timer set", "remind me in", "remind karna"
    ]
    if any(t in u for t in timer_triggers):
        seconds = parse_time_to_seconds(u)

        if seconds == 0:
            # Single number check
            num_match = re.search(r'(\d+)', u)
            if num_match:
                # Default minutes
                seconds = int(num_match.group(1)) * 60

        if seconds == 0:
            speak("Kitne time ka timer lagaun boss?")
            return True

        # Label extract karo
        label = "Timer"
        if "pomodoro" in u:
            label = "Pomodoro"
        elif "break" in u:
            label = "Break"

        start_timer(seconds, label)
        return True

    # POMODORO
    if "focus mode" in u:
        speak("Starting focus mode — 25 minutes focus time, boss.")
        start_timer(25 * 60, "Pomodoro")
        return True

    # CANCEL TIMER
    if any(t in u for t in ["timer cancel", "cancel timer", "timer band karo", "timers cancel"]):
        if active_timers:
            active_timers.clear()
            speak("All timers cancelled, boss.")
        else:
            speak("No timers running.")
        return True