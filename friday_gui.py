import tkinter as tk

root = tk.Tk()
root.title("FRIDAY AI")
root.geometry("500x600")

chat_box = tk.Text(root, font=("Arial", 12))
chat_box.pack(padx=10, pady=10)

def add_message(sender, message):
    chat_box.insert(tk.END, f"{sender}: {message}\n")
    chat_box.see(tk.END)

add_message("FRIDAY", "Hello sir, I am online.")

root.mainloop()