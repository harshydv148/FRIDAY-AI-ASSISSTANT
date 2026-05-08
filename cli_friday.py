import os
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
import pygame
import os
import time
import speech_recognition as sr
import webbrowser
import json
from datetime import datetime

import pyautogui
import pyperclip
import time
import pytesseract
first_start = True
standby_mode = False
last_active_time = time.time()
ACTIVE_DURATION = 20  # seconds


pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Harsh yadav\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Load environment variables
load_dotenv()

#Memory function
def load_memory():
    try:
        with open("memory.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open("memory.json", "w") as f:
        json.dump(memory, f, indent=4)

memory = load_memory()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize voice engine
# engine = pyttsx3.init()
# engine.setProperty('rate', 200)
# engine.setProperty('volume', 1.0)

pygame.mixer.init()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        
        return text
    except:
        print("Sorry, couldn't understand.")
        return None


import os

def find_app(app_name):
    start_menu_paths = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        rf"C:\Users\{os.getlogin()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
    ]

    valid_extensions = (".lnk", ".exe")  #  IMPORTANT

    for path in start_menu_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if app_name.lower() in file.lower() and file.endswith(valid_extensions):
                    return os.path.join(root, file)

    return None


def paste_text(text):
    pyperclip.copy(text)
    time.sleep(1)
    pyautogui.hotkey("ctrl", "v")

def find_file_in_folder(folder_name, file_name):
    base_path = f"C:/Users/{os.getlogin()}/Desktop"

    for root, dirs, files in os.walk(base_path):
        if folder_name.lower() in root.lower():
            for file in files:
                if file_name.lower() in file.lower():
                    return os.path.join(root, file)
    return None

def find_file(file_name):
    search_paths = [
        f"C:/Users/{os.getlogin()}/Desktop",
        f"C:/Users/{os.getlogin()}/Downloads",
        f"C:/Users/{os.getlogin()}/Documents"
    ]

    for path in search_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file_name.lower() in file.lower():
                    return os.path.join(root, file)
    return None

    
def type_text(text):
    time.sleep(2)  # time to switch window
    pyautogui.write(text, interval=0.02)

# def execute_command(action, target):
#     target = target.lower()

#     if action == "open":

#         # 🔥 hardcoded apps first
#         if target == "instagram":
#             os.system("start shell:AppsFolder\\Facebook.InstagramBeta_8xx8rvfyw5nnt!App")
#             speak("Opening Instagram, sir.")
#             return
        
#         if target == "linkedin":
#             os.system("start shell:AppsFolder\\7EE7776C.LinkedInforWindows_w1wdnht996qgy!App")
#             speak("Opening LinkedIn, sir.")
#             return
        
#         if target == "telegram":
#             os.system("start shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop.Store")
#             speak("Opening Telegram, sir.")
#             return

#         # 🔥 fallback system
#         os.system(f"start {target}")
#         speak(f"Opening {target}, sir.")

        
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = "voice.mp3"
        tts.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # wait until audio finishes
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.unload()
        os.remove(filename)

    except Exception as e:
        print("Voice error:", e)


import mss
from PIL import Image

def read_screen():
    with mss.MSS() as sct:
        monitor = sct.monitors[1]

        # 🔥 CUSTOM AREA (adjust kar sakta hai)
        region = {
            "top": 100,
            "left": 0,
            "width": 1200,
            "height": 800
        }

        screenshot = sct.grab(region)

        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        text = pytesseract.image_to_string(img)

        return text

def should_speak(text):
    # ❌ code detect
    if "def " in text or "class " in text:
        return False
    
    # ❌ bohot bada text
    if len(text) > 300:
        return False

    return True
    
# Conversation memory (WITH personality)
conversation = [
    {
        "role": "system",
        "content": "You are FRIDAY, a smart personal AI assistant. You only respond to user commands and queries. Do NOT generate random messages or make assumptions. Keep responses short, clear, and useful. Do not mention fictional characters or create imaginary scenarios."
    }
]

print("FRIDAY (type 'exit' to quit)\n")
print(pytesseract.get_tesseract_version())

is_active = False
last_active_time = time.time()
ACTIVE_DURATION = 20
wake_word = "friday"
voice_mode = False

while True:
    user_input = listen()

    if not user_input:
        continue
    
    last_active_time = time.time()
    print("You:", user_input)

    current_time = time.time()

    #  STANDBY CHECK
    # if not standby_mode and (current_time - last_active_time > ACTIVE_DURATION):
    #     standby_mode = True
    #     print("FRIDAY: (standby mode)")

    if (current_time - last_active_time > ACTIVE_DURATION):
        standby_mode = True
        print("FRIDAY: (standby mode)")
        speak("Going on standby mod , Sir")

    #  WAKE FROM STANDBY
    if standby_mode:
        is_active = True
        if any(phrase in user_input.lower() for phrase in [
            "wake up friday",
            "utho friday",
            "kaam ka waqt",
            "chalo utho friday"
        ]):
            speak("Aapke liye hmesha sir")
            print("FRIDAY: Aapke liye hamesha sir")

            standby_mode = False
            last_active_time = time.time()
            continue
        else:
            continue

    #  WAKE WORD RESPONSE
    if "friday" in user_input.lower():
        
        is_active = True
        if first_start:
            speak("Greeting boss, aaj kya krne ka plan hai")
            print("FRIDAY: Greeting boss, aaj kya krne ka plan hai")
            first_start = False
        else:
            speak("Yes boss, I'm listening")
            print("FRIDAY: Yes boss, I'm listening")

        last_active_time = time.time()

        # remove wake word
        user_input = user_input.lower().replace("friday", "").strip()

        if not user_input:
            continue
    
    #  agar active nahi hai → ignore
    if not is_active:
        continue
    #  GREETING
    if user_input.lower() in ["hello", "hi", "hey"]:
        speak("Hello boss!")
        print("FRIDAY: Hello boss!")
        last_active_time = time.time()
        continue

     
    current_time = time.time()
    
    #  EXPLAIN SCREEN
    if "explain" in user_input.lower() and "screen" in user_input.lower():
        screen_text = read_screen()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Explain this text in simple terms"},
                {"role": "user", "content": screen_text}
            ]
        )

        reply = response.choices[0].message.content

        print("FRIDAY:", reply)

        if should_speak(reply):
            speak(reply)

        last_active_time = time.time()
        continue


    #  MAKE SCREEN PROFESSIONAL
    if "professional" in user_input.lower() and "screen" in user_input.lower():
        screen_text = read_screen()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Rewrite this text in a professional tone"},
                {"role": "user", "content": screen_text}
            ]
        )

        reply = response.choices[0].message.content

        print("FRIDAY:", reply)

        if should_speak(reply):
            speak(reply)

        last_active_time = time.time()
        continue


    if "screen" in user_input.lower():
        screen_text = read_screen()

        #  CLEAN FILTER
        clean_lines = []

        for line in screen_text.split("\n"):
            line = line.strip()

            if len(line) < 5:
                continue

            # ❌ UI garbage words
            if any(word in line.lower() for word in [
                "file", "edit", "view", "windows", "utf", "ln", "col",
                "%", "°", "eng", "start", "merge"
            ]):
                continue

         #  random gibberish (too many weird chars)
            #  gibberish hata (alphabet ratio check)
            alpha_ratio = sum(c.isalpha() for c in line) / len(line)
            if alpha_ratio < 0.5:
                continue

            clean_lines.append(line)

        clean_text = "\n".join(clean_lines)

        print("CLEAN SCREEN:\n", clean_text)

        speak("I've read the screen, sir.")
        last_active_time = time.time()
        continue


    if "summarize screen" in user_input.lower():
        screen_text = read_screen()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Summarize this text"},
                {"role": "user", "content": screen_text}
            ]
        )

        reply = response.choices[0].message.content

        print("FRIDAY:", reply)

        if should_speak(reply):
            speak(reply)
        last_active_time = time.time()
        continue

    if user_input.lower().strip() == "exit":
        speak("Goodbye, sir.")
        print("FRIDAY: Goodbye, sir.")
        break

    #  AUTO MEMORY SAVE
    memory_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
    {
        "role": "system",
        "content": """
You are a memory extraction engine.

Your task:
- Decide if the user's message contains personal information or something important to remember.
- If yes, return ONLY valid JSON.

Format:
{"save": true, "key": "age", "value": "19"}

If nothing should be remembered:
{"save": false}

Rules:
- Save personal preferences, identity, goals, dates, habits, relationships, favorites.
- Save anything user explicitly says to remember.
- Do NOT save technical questions, coding topics, educational content, or commands.
- DO NOT explain anything.
- DO NOT write markdown.
- DO NOT write code.
- Output must be valid JSON only.
"""
    },
    {
        "role": "user",
        "content": user_input
    }
]
    )
    mem_reply = memory_response.choices[0].message.content.strip()

    print("RAW MEMORY:", mem_reply)

    #  remove markdown
    mem_reply = mem_reply.replace("```json", "")
    mem_reply = mem_reply.replace("```python", "")
    mem_reply = mem_reply.replace("```", "")

    #  extract only JSON
    start = mem_reply.find("{")
    end = mem_reply.rfind("}") + 1

    if start == -1 or end == 0:
        print("INVALID MEMORY OUTPUT")
        continue

    mem_reply = mem_reply[start:end]

    print("CLEAN MEMORY:", mem_reply)
##----------------------------------------------------------------
    mem_reply = mem_reply.strip()

    #  code block hatao
    if mem_reply.startswith("```"):
        mem_reply = mem_reply.split("```")[1]

    #  extra text hatao (last JSON extract)
    start = mem_reply.find("{")
    end = mem_reply.rfind("}") + 1

    if start != -1 and end != -1:
        mem_reply = mem_reply[start:end]

    try:
        data = json.loads(mem_reply)
        save_memory_flag = data.get("save")
        key = data.get("key")
        value = data.get("value")
        
        if save_memory_flag and key and value:
            #  ignore invalid
            if not key or not value:
                continue

            #  ignore long garbage
            if len(value) > 100:
                continue

            #  ignore questions
            if "?" in user_input:
                continue

            # #  ignore technical words
            # blocked_words = ["algorithm", "code", "time complexity", "merge", "python"]

            # if any(word in user_input.lower() for word in blocked_words):
            #     continue

            memory[key] = value
            save_memory(memory)

            print("🧠 Saved:", key, "=", value)

            speak(f"Got it boss, I'll remember that.")
            continue   
    except Exception as e:
        print("MEMORY ERROR:", e)

    
    #  Activate if wake word used
    if not is_active and wake_word in user_input.lower():
        is_active = True
        last_active_time = current_time
        speak("Yes sir, I'm listening.")

        # remove wake word
        user_input = user_input.lower().replace(wake_word, "").strip()

    #  agar active nahi hai → ignore
    elif not is_active:
        continue

        # Check timeout
    if current_time - last_active_time > ACTIVE_DURATION:
        is_active = False
        speak("Going back to standby mode, sir.")
        continue

    #  update active time (VERY IMPORTANT)
    last_active_time = current_time
    
    # if user_input.lower() == "exit":
    #     speak("Goodbye, sir.")
    #     print("FRIDAY: Goodbye, sir.")
    #     break

#-----commands start -------------------------------------------
    import webbrowser
    

    if "day" in user_input.lower() or "date" in user_input.lower():
        now = datetime.now()

        day = now.strftime("%A")
        date = now.strftime("%d %B %Y")

        speak(f"Today is {day}, {date}, sir.")
        print(f"FRIDAY: Today is {day}, {date}, sir.")
        last_active_time = time.time()
        continue

    if user_input.strip().lower() in ["time", "what time is it", "current time"]:
        current_time = datetime.now().strftime("%H:%M")
        speak(f"The time is {current_time}, sir.")
        last_active_time = time.time()
        continue

    if "good morning" in user_input.lower():
        speak("Good morning, sir. Hope you're ready to conquer the day.")
        last_active_time = time.time()
        continue
    
    import os

#-----APPS COMMANDS-------------->

    import subprocess

    # if user_input.lower().startswith("open"):
    #     app_name = user_input.lower().replace("open", "").strip()

    #     app_path = find_app(app_name)

    #     if app_path:
    #         os.startfile(app_path)
    #         speak(f"Opening {app_name}, sir.")
    #     else:
    #         speak(f"I couldn't find {app_name}, sir.")

    #     continue

#---------Websiteee search commands--------->
    if "search" in user_input.lower():
        query = user_input.lower().replace("search", "")
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        speak(f"Searching for {query}, sir.")
        last_active_time = time.time()
        continue

    # import os

    # if user_input.lower().startswith("open"):
    #     app_name = user_input.lower().replace("open", "").strip()

    #     try:
    #         os.system(f"start {app_name}")
    #         speak(f"Opening {app_name}, sir.")
    #     except:
    #         speak(f"Sorry sir, I couldn't find {app_name}.")
    
    #     continue


    if "open youtube" in user_input.lower():
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube, sir.")
        last_active_time = time.time()
        continue

    if "open google" in user_input.lower():
        webbrowser.open("https://google.com")
        speak("Opening Google, sir.")
        last_active_time = time.time()
        continue

    if "open notepad" in user_input.lower():
        os.system("notepad")
        speak("Opening Notepad, sir.")
        last_active_time = time.time()
        continue

    # if "open chrome" in user_input.lower():
    #     os.system("start chrome")
    #     speak("Opening Chrome, sir.")
    #     last_active_time = time.time()
    #     continue

    if "open code" in user_input.lower() or "open vs code" in user_input.lower():
        os.system("code")
        speak("Opening VS Code, sir.")
        last_active_time = time.time()
        continue

    if "open telegram" in user_input.lower():
        os.system("start shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop.Store")
        speak("Opening Telegram, sir.")
        continue

    if "open instagram" in user_input.lower():
        os.system("start shell:AppsFolder\\Facebook.InstagramBeta_8xx8rvfyw5nnt!App")
        speak("Opening Instagram, sir.")
        continue

    if "open linkedin" in user_input.lower():
        os.system("start shell:AppsFolder\\7EE7776C.LinkedInforWindows_w1wdnht996qgy!App")
        speak("Opening LinkedIn, sir.")
        continue


    if "study mode" in user_input.lower():
        speak("Activating study mode, sir.")

        links = [
            "https://leetcode.com/",
            "https://chat.openai.com",
            "https://www.apnacollege.in/start",
            "https://github.com"
        ]

        for link in links:
            webbrowser.open_new_tab(link)
        last_active_time = time.time()
        continue

#------OS commands-----

    if "open downloads" in user_input.lower():
        os.startfile("C:\\Users\\Harsh yadav\\Downloads")
        speak("Opening downloads, sir.")
        last_active_time = time.time()
        continue

    if "open desktop" in user_input.lower():
        os.startfile("C:\\Users\\Harsh yadav\\Desktop") 
        speak("Opening desktop, sir.")
        last_active_time = time.time()
        continue

    if user_input.lower().startswith("open"):
        text = user_input.lower().replace("open", "").strip()

        # CASE 1
        if "from" in text and "folder" in text:
            parts = text.split("from")

            file_name = parts[0].strip()
            folder_name = parts[1].replace("folder", "").strip()

            file_path = find_file_in_folder(folder_name, file_name)

            if file_path:
                os.startfile(file_path)
                speak(f"Opening {file_name} from {folder_name}, sir.")
            else:
                speak(f"I couldn't find {file_name} in {folder_name}, sir.")

        else:
            # CASE 2
            file_path = find_file(text)

            if file_path:
                os.startfile(file_path)
                speak(f"Opening {text}, sir.")
            else:
                # CASE 3
                app_path = find_app(text)

                if app_path:
                    os.startfile(app_path)
                    speak(f"Opening {text}, sir.")
                    continue

                #  CASE 4: fallback (IMPORTANT)
                os.system(f"start {text}")
                speak(f"Trying to open {text}, sir.")

        continue


    if "shutdown" in user_input.lower():
        speak("Shutting down the system, sir.")
        os.system("shutdown /s /t 5")
        continue

    if "restart system" in user_input.lower():
        speak("Restarting the system, sir.")
        os.system("shutdown /r /t 5")
        continue
    #---------COMMANDS over --------

    # Add user message to memory
    conversation.append({
        "role": "user",
        "content": user_input
    })

    # 🔥 AI INTENT DETECTION
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
    You are an AI that extracts intent.

    If the user gives a command like 'open youtube', return JSON:
    {"action": "open", "target": "youtube"}

    If it's not a command (like hello, hi, friday), return:
    {"action": null, "target": null}

    ONLY return JSON. No extra text.
    """
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    reply = response.choices[0].message.content

    import json

    try:
        data = json.loads(reply)
        action = data.get("action")
        target = data.get("target")

        if action and target:
            execute_command(action, target)
            continue
    #  CASE 2: null → normal AI reply chahiye
        else:
        #  yaha NORMAL AI call kar
            normal_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"""
            You are FRIDAY, a smart AI assistant.

            User info: {memory}

            Rules:
            - Only respond if the user gives a clear instruction or question.
            - If input is unclear (like 'friday', 'hello', single word), DO NOT respond.
            - Do NOT give default replies like date/time unless asked.
            - Be short, helpful, and to the point.
            """
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            )

            final_reply = normal_response.choices[0].message.content

            print("FRIDAY:", final_reply)

            #  useless replies block
            bad_phrases = [
                "no instruction",
                "you haven't provided",
                "please provide",
            ]

            if any(phrase in final_reply.lower() for phrase in bad_phrases):
                print("FRIDAY: (ignored useless reply)")
                continue

            if should_speak(final_reply):
                speak(final_reply)

            if "write" in user_input.lower() or "type" in user_input.lower():
                time.sleep(1)
                paste_text(final_reply)
            conversation.append({"role": "assistant", "content": final_reply})

            continue

    except:
        pass