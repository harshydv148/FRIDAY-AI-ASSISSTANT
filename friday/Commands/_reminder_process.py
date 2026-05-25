
import time
from datetime import datetime

target = datetime.strptime("2026-05-19 10:54:05", "%Y-%m-%d %H:%M:%S")
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
    print(f"Beep error: {e}")

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
        text="1 minut mein remind",
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
    print(f"Popup error: {e}")

# Voice reminder
try:
    import pygame
    from gtts import gTTS
    import os
    import uuid

    pygame.mixer.init()
    tts = gTTS(text="Boss, reminder. 1 minut mein remind", lang="en")
    filename = f"rem_{uuid.uuid4().hex[:6]}.mp3"
    tts.save(filename)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()
    os.remove(filename)
except Exception as e:
    print(f"Voice error: {e}")
