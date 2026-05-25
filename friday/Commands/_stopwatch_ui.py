
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
