import os
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
import pygame
import time
import speech_recognition as sr
import webbrowser
import json
from datetime import datetime
import uuid
import sys
import webbrowser
import pyautogui
import pyperclip
import time
import pytesseract
import mss
from PIL import Image


class FridayState:
    def __init__(self):
        self.active = False
        self.last_active = time.time()
        self.first_start = True
        self.standby = False
        self.TIMEOUT = 20

    def wake(self):
        self.active = True
        self.standby = False
        self.last_active = time.time()

    def touch(self):
        self.last_active = time.time()

    def is_timed_out(self):
        return time.time() - self.last_active > self.TIMEOUT

    def go_standby(self):
        self.active = False
        self.standby = True

state = FridayState()


USERNAME = os.getlogin()
pytesseract.pytesseract.tesseract_cmd = rf"C:\Users\{USERNAME}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
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

WEB_APPS = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "github": "https://github.com",
    "problems": "https://leetcode.com",
    "gpt": "https://chat.openai.com",
    "instagram": "https://instagram.com",
    "linkedin": "https://linkedin.com",
    "twitter": "https://twitter.com",
    "gmail": "https://mail.google.com",
}


SYSTEM_APPS = {
    "notepad": "notepad",
    "vs code": "code",
    "code": "code",
    "telegram": "start shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop.Store",
    "calculator": "calc",
    "paint": "mspaint",
    "task manager": "taskmgr",
}

BROWSER_APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
}

APP_FIRST = {
            "instagram": {
                "app": "start shell:AppsFolder\\Facebook.InstagramBeta_8xx8rvfyw5nnt!App",
                "web": "https://instagram.com"
            },
            "whatsapp": {
                "app": "start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
                "web": "https://web.whatsapp.com"
            },
            "telegram": {
                "app": "start shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop.Store",
                "web": "https://web.telegram.org"
            },
            "linkedin": {
                "app": "start shell:AppsFolder\\7EE7776C.LinkedInforWindows_w1wdnht996qgy!App",
                "web": "https://linkedin.com"
            },
            "snapchat": {
                "app": "start shell:AppsFolder\\CBSInteractive.Snapchat_kzf8qxf38zg5c!App",
                "web": "https://snapchat.com"
            },
            "spotify": {
                "app": "start shell:AppsFolder\\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
                "web": "https://open.spotify.com"
            },
            "twitter": {
                "app": "start shell:AppsFolder\\Twitter.Twitter_8xx8rvfyw5nnt!App",
                "web": "https://twitter.com"
            },
            "gpt":{
                "app": "start shell:AppsFolder\\OpenAI.ChatGPT-Desktop_2p2nqsd0c76g0!ChatGPT",
                "web": "https://chat.openai.com"
            },
        }


import psutil
import os

def get_protected_pids():
    my_pid = os.getpid()
    protected = set()
    
    try:
        # Apni poori family tree protect karo
        me = psutil.Process(my_pid)
        protected.add(my_pid)
        
        # Upar tak — parents
        try:
            p = me.parent()
            while p:
                protected.add(p.pid)
                p = p.parent()
        except:
            pass
        
        # Neeche tak — children
        try:
            for c in me.children(recursive=True):
                protected.add(c.pid)
        except:
            pass
            
    except:
        protected.add(my_pid)
    
    return protected


def get_all_protected_names():
    """Process names jo kabhi band nahi honge"""
    return {
        "code.exe", "code - insiders.exe",
        "cmd.exe", "powershell.exe", "powershell_ise.exe",
        "windowsterminal.exe", "wt.exe",
        "python.exe", "pythonw.exe", "python3.exe",
        "conhost.exe", "openconsole.exe",
        "explorer.exe", "taskmgr.exe",
        "node.exe", "electron.exe",
        # System critical
        "system", "smss.exe", "csrss.exe", "wininit.exe",
        "winlogon.exe", "services.exe", "lsass.exe",
        "svchost.exe", "dwm.exe", "fontdrvhost.exe",
        "registry", "tasklist.exe", "taskkill.exe",
        "sihost.exe", "ctfmon.exe", "spoolsv.exe",
        "runtimebroker.exe", "dllhost.exe", "audiodg.exe",
        "searchhost.exe", "searchindexer.exe",
        "shellexperiencehost.exe", "startmenuexperiencehost.exe",
        "textinputhost.exe", "applicationframehost.exe",
        "backgroundtaskhost.exe", "taskhostw.exe",
        "securityhealthservice.exe", "securityhealthsystray.exe",
        "msmpeng.exe", "nissrv.exe", "msiexec.exe",
        "smartscreen.exe", "lockapp.exe",
    }


def close_all_apps():
    protected_pids = get_protected_pids()
    protected_names = get_all_protected_names()
    
    print(f"🛡️ My PID chain: {protected_pids}")
    
    closed = []
    skipped = []
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.info['pid']
            name = proc.info['name'].lower()
            
            # PID protected hai?
            if pid in protected_pids:
                skipped.append(f"{name}({pid})")
                continue
            
            # Name protected hai?
            if name in protected_names:
                continue
                
            # Band karo
            proc.kill()
            closed.append(name)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            continue
    
    print(f"✅ Closed: {list(set(closed))}")
    print(f"🛡️ Skipped (protected): {skipped}")
    
    if closed:
        speak("All background apps closed, sir.")
    else:
        speak("No apps to close, sir.")


def close_specific_apps(app_names_to_keep: list):
    protected_pids = get_protected_pids()
    protected_names = get_all_protected_names()
    
    APP_ALIASES = {
        "calculator": ["calc.exe", "calculator.exe", "calculatorapp.exe"],
        "chrome": ["chrome.exe"],
        "firefox": ["firefox.exe"],
        "spotify": ["spotify.exe"],
        "discord": ["discord.exe"],
        "telegram": ["telegram.exe"],
        "vlc": ["vlc.exe"],
        "notepad": ["notepad.exe"],
        "word": ["winword.exe"],
        "excel": ["excel.exe"],
        "whatsapp": ["whatsapp.exe"],
        "zoom": ["zoom.exe"],
        "obs": ["obs64.exe", "obs.exe"],
        "steam": ["steam.exe"],
        "brave": ["brave.exe"],
        "edge": ["msedge.exe"],
    }
    
    user_protected = [a.lower().strip() for a in app_names_to_keep]
    
    closed = []
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.info['pid']
            name = proc.info['name'].lower()
            
            if pid in protected_pids:
                continue
                
            if name in protected_names:
                continue
            
            # User ke specified apps skip karo
            skip = False
            for u_app in user_protected:
                aliases = APP_ALIASES.get(u_app, [u_app + ".exe", u_app])
                if any(alias.lower() in name for alias in aliases):
                    skip = True
                    break
            
            if skip:
                continue
            
            proc.kill()
            closed.append(name)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception:
            continue
    
    kept = ', '.join(app_names_to_keep)
    print(f"✅ Closed all except: {kept}")
    speak(f"Done sir, kept {kept} running.")


def close_all_tabs():
    """Chrome gracefully close karo"""
    import subprocess
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq chrome.exe'],
            capture_output=True, text=True
        )
        if 'chrome.exe' not in result.stdout.lower():
            speak("Chrome is not running, sir.")
            return
            
        subprocess.run(
            ['powershell', '-command',
             '$wshell = New-Object -ComObject wscript.shell; '
             'Get-Process chrome | ForEach-Object { $_.CloseMainWindow() }'],
            capture_output=True, timeout=5
        )
        speak("Chrome closed, sir.")
    except Exception as e:
        print("Chrome close error:", e)
        speak("Couldn't close Chrome, sir.")

def close_current_tab():
    import pyautogui
    try:
        pyautogui.hotkey('ctrl', 'w')
        speak("Tab closed, sir.")
    except Exception as e:
        print("Tab close error:", e)

def close_current_window():
    import pyautogui
    try:
        pyautogui.hotkey('alt', 'f4')
        speak("Window closed, sir.")
    except Exception as e:
        print("Window close error:", e)

memory = load_memory()

def refresh_memory():
    global memory
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

def execute_command(action, target):
    target = target.lower()

    if action == "open":

        # 🔥 hardcoded apps first
        if target == "instagram":
            os.system("start shell:AppsFolder\\Facebook.InstagramBeta_8xx8rvfyw5nnt!App")
            speak("Opening Instagram, sir.")
            return
        
        if target == "linkedin":
            os.system("start shell:AppsFolder\\7EE7776C.LinkedInforWindows_w1wdnht996qgy!App")
            speak("Opening LinkedIn, sir.")
            return
        
        if target == "telegram":
            os.system("start shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop.Store")
            speak("Opening Telegram, sir.")
            return

        # 🔥 fallback system
        os.system(f"start {target}")
        speak(f"Opening {target}, sir.")

        
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = f"voice_{uuid.uuid4().hex[:8]}.mp3"
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        os.remove(filename)
    except Exception as e:
        print("Voice error:", e)
        # cleanup agar file reh gayi ho
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

def read_screen():
    import re
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img = img.convert("L")
        raw_text = pytesseract.image_to_string(img)

        clean_lines = []
        for line in raw_text.split("\n"):
            line = line.strip()

            # Too short
            if len(line) < 8:
                continue

            # Has file extension — title bar
            if re.search(r'\b\w+\.(txt|py|pdf|docx|xlsx|jpg|png|mp4|exe|json)\b', line, re.IGNORECASE):
                continue

            # Menu bar — 2+ menu words
            menu_words = {"file", "edit", "view", "insert", "format",
                         "tools", "help", "window", "ht", "h1", "bis"}
            line_words_lower = set(line.lower().split())
            if len(line_words_lower.intersection(menu_words)) >= 2:
                continue

            # Status bar — Ln, Col, UTF, CRLF
            if re.search(r'\bLn\b|\bCol\b|\bUTF\b|\bCRLF\b|\bENG\b', line):
                continue

            # Has % — status bar
            if "%" in line:
                continue

            # Temperature
            if re.search(r'\d+°', line):
                continue

            # Weather
            if any(w in line.lower() for w in ["sunny", "cloudy", "rainy", "windy", "humid"]):
                continue

            # Date pattern — 11-05-2026
            if re.search(r'\d{2}-\d{2}-\d{4}', line):
                continue

            # Too many symbols
            symbol_count = sum(1 for c in line if c in '@*#^~`[]{}|\\<>()°©®™$&_+=/')
            if symbol_count > 2:
                continue

            # Low alpha ratio
            alpha_ratio = sum(c.isalpha() for c in line) / len(line)
            if alpha_ratio < 0.5:
                continue

            # Taskbar line — Q Search
            if line.lower().startswith("q "):
                continue

            clean_lines.append(line)

        clean_text = "\n".join(clean_lines).strip()
        return clean_text

def should_speak(text):
    # Code blocks mat bolo
    if "```" in text:
        return False
    # Pure code detect karo
    code_lines = sum(1 for line in text.split('\n') 
                    if line.strip().startswith(('def ', 'class ', 'import ', 
                                               'for ', 'if ', 'while ', '#')))
    if code_lines > 3:
        return False
    # Bohot lamba text truncate karke bolo
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

wake_word = "friday"

while True:
    user_input = listen()

    if not user_input:
        continue
    
    state.touch()
    print("You:", user_input)

    if state.is_timed_out() and not state.standby:
        state.go_standby()
        print("FRIDAY: (standby mode)")
        speak("Going on standby, Sir.")

        
    #  WAKE FROM STANDBY
    if state.standby:
        if any(phrase in user_input.lower() for phrase in [
            "wake up friday",
            "utho friday",
            "kaam ka waqt",
            "chalo utho friday"
        ]):
            state.wake()
            speak("Aapke liye hamesha sir.")
            print("FRIDAY: Aapke liye hamesha sir")
            continue
        else:
            continue

    #  WAKE WORD RESPONSE
    if "friday" in user_input.lower():
        state.wake()
        if state.first_start:
            speak("Greeting boss, aaj kya krne ka plan hai.")
            print("FRIDAY: Greeting boss, aaj kya krne ka plan hai")
            state.first_start = False
        else:
            speak("Yes boss, I'm listening.")
            print("FRIDAY: Yes boss, I'm listening")

        # remove wake word
        user_input = user_input.lower().replace("friday", "").strip()

        if not user_input:
            continue
    
    #  agar active nahi hai → ignore
    if not state.active:
        continue
    #  GREETING

    if user_input.lower() in ["hello", "hi", "hey"]:
        speak("Hello boss!")
        print("FRIDAY: Hello boss!")
        state.touch()
        continue

     
    current_time = time.time()
    
    #  EXPLAIN SCREEN
    # SCREEN COMMANDS - order matters!
    
    # Sirf "explain" ya "summarize" akela aaye — ignore karo
    solo_words = {
        "explain": "explain screen bolo boss.",
        "summarize": "summarise screen bolo boss.",
        "summarise": "summarise screen bolo boss.",
        "professional": "make screen professional bolo boss.",
        "read": "read screen bolo boss.",
        "bright": "Kya karna hai boss? Thoda clear karo.",
        "screen": "Kya karna hai screen ke saath boss? Explain, summarise, ya professional?",
    }
    if user_input.lower().strip() in solo_words:
        speak(solo_words[user_input.lower().strip()])
        state.touch()
        continue


    summarise_triggers = [
        "summarize screen", "summarise screen",
        "summarize the screen", "summarise the screen",
        "screen summarize", "screen summarise",
        "screen ko summarize", "screen summary"
    ]
    if any(t in user_input.lower() for t in summarise_triggers):
        screen_text = read_screen()
        if not screen_text.strip():
            speak("Screen pe kuch readable nahi mila boss.")
            state.touch()
            continue
            
        sum_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a voice assistant. Summarize the screen content.
STRICT RULES:
- Summarize ONLY what is written in the text provided.
- Do NOT use any memory or personal info about the user.
- Do NOT mention file names, menus, or UI elements.
- 2 sentences max.
- Start with "Boss,"
- Speak naturally, no bullet points.
"""
                },
                {
                    "role": "user",
                    "content": f"Summarize this screen content:\n\n{screen_text}"
                }
            ]
        )
        reply = sum_response.choices[0].message.content
        sentences = [s.strip() for s in reply.replace('\n', ' ').split('.') if s.strip()]
        short_reply = '. '.join(sentences[:2]) + '.' if sentences else reply
        print("FRIDAY:", short_reply)
        speak(short_reply)
        state.touch()
        continue

    explain_triggers = [
        "explain screen", "plain screen", "a plane screen",
        "explain the screen", "screen explain", "screen ko explain",
        "bright screen", "screen bright",  # speech recognition variations
        "screen batao", "screen kya hai", "screen dekho"
    ]
    if any(t in user_input.lower() for t in explain_triggers):
        screen_text = read_screen()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": """
You are a voice assistant. Explain what you see in this screen text.
Rules:
- Speak naturally, no bullet points, no lists, no markdown.
- STRICT 2 sentences only — no more.
- Don't say words like "corrupted", "truncated", "incomplete".
- Just describe what the content is about simply.
- Start with "Boss," 
- Example: "Boss, this looks like a resume belonging to Harsh, a BCA student who enjoys cricket and programming."
"""},
                {"role": "user", "content": screen_text}
            ]
        )
        reply = response.choices[0].message.content
        print("FRIDAY:", reply)
        if should_speak(reply):
            # Pehli 2 sentences nikalo
            sentences = [s.strip() for s in reply.replace('\n', ' ').split('.') if s.strip()]
            short_reply = '. '.join(sentences[:2]) + '.' if sentences else reply
            speak(short_reply)
            print("FRIDAY (spoken):", short_reply)
        state.touch()
        continue

    print(f"DEBUG: user_input='{user_input}', professional={('professional' in user_input.lower())}, screen={('screen' in user_input.lower())}")
    if "professional" in user_input.lower() and "screen" in user_input.lower():
        screen_text = read_screen()
        print("📄 SCREEN TEXT GOING TO LLM:\n", screen_text)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": """
                You are a professional writing assistant.
                Your ONLY job: rewrite the text the user gives you in a professional tone.

                STRICT RULES:
                    - Rewrite EACH AND EVERY line/sentence from the input.
                    - Do NOT skip any line, any name, any fact.
                    - Do NOT summarize — rewrite fully.
                    - Do NOT add any intro like "Here is..." or "The following..."
                    - Output ONLY the rewritten professional text. Nothing else.

                Example:
                Input:
                My name is Harsh. I am a BCA student.
                I like cricket and programming.

                Output:
                My name is Harsh, and I am currently pursuing a Bachelor of Computer Applications (BCA) degree.
                I have a keen interest in cricket and computer programming.
                """},
                        {"role": "user", "content": f"Rewrite this text professionally, every single line:\n\n{screen_text}"}
                    ]
                )
        reply = response.choices[0].message.content
        print("FRIDAY:", reply)
        if should_speak(reply):
            sentences = [s.strip() for s in reply.replace('\n', ' ').split('.') if s.strip()]
            short_reply = '. '.join(sentences[:2]) + '.' if sentences else reply
            speak(short_reply)
            print("FRIDAY (spoken):", short_reply)
        
        # Notepad mein paste karo
        import pygetwindow as gw
        import time
        
        # Notepad window dhundho
        notepad_windows = [w for w in gw.getAllWindows() 
                          if 'notepad' in w.title.lower() or '.txt' in w.title.lower()]
        
        if notepad_windows:
            notepad_windows[0].activate()
            time.sleep(0.8)  # window focus hone do
            
            # Pehle sab select karo phir delete karo
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.2)
            
            # Poora reply clipboard mein daalo aur paste karo
            pyperclip.copy(reply)
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            speak("Done boss, notepad updated.")
        else:
            speak("Notepad nahi mili boss, manually paste karo — Ctrl V.")
            pyperclip.copy(reply)
        
        state.touch()
        continue

    if "read screen" in user_input.lower() or "screen padho" in user_input.lower():
        screen_text = read_screen()
        print("CLEAN SCREEN:\n", screen_text)
        speak("I've read the screen, sir.")
        state.touch()
        continue

    if user_input.lower().strip() == "exit":
        speak("Goodbye, sir.")
        print("FRIDAY: Goodbye, sir.")
        break

    #  AUTO MEMORY SAVE
    # AUTO MEMORY SAVE - Smart version
    explicit_keywords = [
        "remember", "yaad rakh", "save this", "note this",
        "save karo", "yaad karo", "remember this", "store this",
        "isey yaad rkhna", "yeh save karo"
    ]

    explicit_save = any(kw in user_input.lower() for kw in explicit_keywords)

    should_check_memory = False

    if explicit_save:
        should_check_memory = True
    else:
        u = user_input.lower().strip()
        personal_hints = [
            "my ", "mera ", "meri ", "i am ", "i'm ", "main hoon",
            "mera naam", "my name", "my age", "i live",
            "i like ", "i love ", "i hate ", "i enjoy ", "i prefer ",
            "my favourite", "my favorite", "mujhe pasand", "mujhe nahi pasand",
            "i study", "i work", "i am a", "main ek",
            "my hobby", "my goal", "i want to", "i use",
            "my city", "my college", "my school", "i play", "i watch",
            "mera favourite", "meri favourite", "mujhe ", "i don't like"
        ]
        if any(hint in u for hint in personal_hints):
            should_check_memory = True
        # 4 word condition hatai - ab direct hint check kaafi hai   

    if should_check_memory:
        memory_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a memory extraction engine for a personal AI assistant.

Your ONLY job: decide if this message contains a personal fact about the user.

ALWAYS SAVE these patterns (save: true):
- "I like X" → favourite or preference
- "I love X" → favourite or preference  
- "I hate X" → dislike
- "I enjoy X" → hobby or preference
- "I play X" → hobby
- "I watch X" → hobby
- "I am X years old" → age
- "I am a X" → education or job
- "I work at X" → job
- "I live in X" → city
- "My name is X" → name
- "I study X" → education
- "My favourite X is Y" → favourite_X
- "I prefer X" → preference
- "mujhe X pasand hai" → favourite or preference
- "mera X hai" → personal info
- "remember X" → whatever X is

NEVER SAVE:
- Pure questions ("what is", "how to", "why")
- Commands ("open", "search", "play")
- Random numbers with no context ("14", "2006")
- General knowledge ("what is python")

KEY NAMING - always specific:
- like/love food → "favourite_food"
- like/love sport → "favourite_sport"  
- like/love music/artist/song → "favourite_music"
- like/love movie → "favourite_movie"
- like/love colour → "favourite_colour"
- like/love game → "favourite_game"
- hobby/enjoy/play → "hobby"
- age → "age"
- city/live in → "city"
- name → "name"
- job/work → "job"
- education/student → "education"
- hate/dislike → "dislike"

Examples:
"I like burger" → {"save": true, "key": "favourite_food", "value": "burger"}
"I like burgers" → {"save": true, "key": "favourite_food", "value": "burger"}
"I love cricket" → {"save": true, "key": "favourite_sport", "value": "cricket"}
"I am 19 years old" → {"save": true, "key": "age", "value": "19"}
"I am a BCA student" → {"save": true, "key": "education", "value": "BCA student"}
"open youtube" → {"save": false}
"what is python" → {"save": false}
"2006" → {"save": false}
"I like playing games" → {"save": true, "key": "hobby", "value": "playing games"}

Return ONLY valid JSON. No explanation. No extra text.
"""
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        mem_reply = memory_response.choices[0].message.content.strip()
        print("🔍 RAW MEMORY RESPONSE:", mem_reply)
        mem_reply = mem_reply.replace("```json", "").replace("```python", "").replace("```", "")

        start = mem_reply.find("{")
        end = mem_reply.rfind("}") + 1
        if start != -1 and end != 0:
            mem_reply = mem_reply[start:end].strip()
            try:
                data = json.loads(mem_reply)
                save_memory_flag = data.get("save")
                key = data.get("key")
                value = data.get("value")

                if save_memory_flag and key and value:
                    if len(value) <= 100:
                        memory[key] = value
                        save_memory(memory)
                        refresh_memory()
                        print("🧠 Saved:", key, "=", value)
                        speak(f"Got it boss, I'll remember that your {key} is {value}.")
                        continue
                    
                # LLM ne save=false kaha matlab personal info nahi thi
                # Normal AI response pe jaane do, continue mat karo
                        
            except Exception as e:
                print("MEMORY ERROR:", e)

    #  update active time (VERY IMPORTANT)
    state.touch()
    
    # if user_input.lower() == "exit":
    #     speak("Goodbye, sir.")
    #     print("FRIDAY: Goodbye, sir.")
    #     break

#-----commands start -------------------------------------------    

    if "day" in user_input.lower() or "date" in user_input.lower():
        now = datetime.now()

        day = now.strftime("%A")
        date = now.strftime("%d %B %Y")

        speak(f"Today is {day}, {date}, sir.")
        print(f"FRIDAY: Today is {day}, {date}, sir.")
        state.touch()
        continue

    time_triggers = [
        "time", "what time", "current time", "kitne baje",
        "time kya", "kya time", "time kya hai", "time kya hua",
        "time batao", "time bolo", "abhi kitne baje hain",
        "what's the time", "baje hain"
    ]
    if any(t in user_input.lower() for t in time_triggers):
        now = datetime.now()
        hour = now.strftime("%I")
        minute = now.strftime("%M")
        ampm = now.strftime("%p")
        speak(f"It's {hour}:{minute} {ampm}, boss.")
        state.touch()
        continue
    
    if user_input.lower().startswith("type "):
        type_request = user_input[5:].strip()
        
        type_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a writing assistant. User will ask you to type something.
Generate the appropriate content based on the request.

RULES:
- If user says "type merge sort" → write the full merge sort algorithm with code
- If user says "type a mail to boss" → write a professional email
- If user says "type selection sort" → write selection sort code
- If user says "type an apology letter" → write a full apology letter
- Just output the content directly — no explanation, no intro like "Here is..."
- Output only what should be typed, nothing else.
"""
                },
                {
                    "role": "user",
                    "content": f"Type this for me: {type_request}"
                }
            ]
        )
        
        generated_text = type_response.choices[0].message.content
        print("FRIDAY (typing):", generated_text[:100], "...")
        speak(f"Typing {type_request} for you, boss.")
        time.sleep(1)
        paste_text(generated_text)
        state.touch()
        continue

    if "good morning" in user_input.lower():
        speak("Good morning boss! Hope you're ready to conquer the day.")
        state.touch()
        continue

    if "good evening" in user_input.lower():
        speak("Good evening boss! What are we working on tonight?")
        state.touch()
        continue

    if "good night" in user_input.lower():
        speak("Good night boss! Get some rest.")
        state.touch()
        continue

    if "good afternoon" in user_input.lower():
        speak("Good afternoon boss! What can I do for you?")
        state.touch()
        continue
    
    import os


#---------Websiteee search commands--------->

    if user_input.lower().startswith("open"):
        target = user_input.lower().replace("open", "").strip()

        if not target:
            speak("Kya kholna hai boss?")
            state.touch()
            continue

        # 1. Browser direct path se kholo
        if target in BROWSER_APPS:
            browser_path = BROWSER_APPS[target]
            if os.path.exists(browser_path):
                os.startfile(browser_path)
                speak(f"Opening {target}, boss.")
            else:
                os.system(f"start {target}")
                speak(f"Opening {target}, boss.")
            state.touch()
            continue

        # 2. Store apps / APP_FIRST
        if target in APP_FIRST:
            app_cmd = APP_FIRST[target]["app"]
            web_url = APP_FIRST[target]["web"]
            try:
                result = os.system(app_cmd)
                if result != 0:
                    webbrowser.open(web_url)
                    speak(f"App nahi mili, opening {target} in browser, boss.")
                else:
                    speak(f"Opening {target}, boss.")
            except:
                webbrowser.open(web_url)
                speak(f"Opening {target} in browser, boss.")
            state.touch()
            continue

        # 3. Web apps
        if target in WEB_APPS:
            webbrowser.open(WEB_APPS[target])
            speak(f"Opening {target}, boss.")
            state.touch()
            continue

        # 4. System apps
        if target in SYSTEM_APPS:
            os.system(SYSTEM_APPS[target])
            speak(f"Opening {target}, boss.")
            state.touch()
            continue

        # 5. Common apps — file search mat karo
        common_apps = {
            "chrome", "firefox", "edge", "brave", "spotify",
            "discord", "telegram", "whatsapp", "instagram",
            "notepad", "calculator", "paint", "zoom", "vlc",
            "steam", "obs", "word", "excel"
        }

        if target not in common_apps:
            # File dhundho
            if "from" in target and "folder" in target:
                parts = target.split("from")
                file_name = parts[0].strip()
                folder_name = parts[1].replace("folder", "").strip()
                file_path = find_file_in_folder(folder_name, file_name)
                if file_path:
                    os.startfile(file_path)
                    speak(f"Opening {file_name}, boss.")
                    state.touch()
                    continue
            
            file_path = find_file(target)
            if file_path:
                os.startfile(file_path)
                speak(f"Opening {target}, boss.")
                state.touch()
                continue

        # 6. find_app se dhundho — common apps ke liye bhi
        app_path = find_app(target)
        if app_path:
            os.startfile(app_path)
            speak(f"Opening {target}, boss.")
            state.touch()
            continue

        # 7. Last fallback
        os.system(f"start {target}")
        speak(f"Trying to open {target}, boss.")
        state.touch()
        continue

        if target in WEB_APPS:
            webbrowser.open(WEB_APPS[target])
            speak(f"Opening {target}, sir.")
            state.touch()
            continue
        elif target in SYSTEM_APPS:
            os.system(SYSTEM_APPS[target])
            speak(f"Opening {target}, sir.")
            state.touch()
            continue
        else:
            text = target
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
                file_path = find_file(text)
                if file_path:
                    os.startfile(file_path)
                    speak(f"Opening {text}, sir.")
                else:
                    app_path = find_app(text)
                    if app_path:
                        os.startfile(app_path)
                        speak(f"Opening {text}, sir.")
                    else:
                        os.system(f"start {text}")
                        speak(f"Trying to open {text}, sir.")
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
        state.touch()
        continue

#------OS commands-----

    if "open downloads" in user_input.lower():
        os.startfile(os.path.expanduser("~\\Downloads"))
        speak("Opening downloads, sir.")
        state.touch()
        continue

    if "open desktop" in user_input.lower():
        os.startfile(os.path.expanduser("~\\Desktop"))
        speak("Opening desktop, sir.")
        state.touch()
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

# CLOSE ALL TABS - Chrome ke saare tabs band karo
    if "close all tab" in user_input.lower():
        u = user_input.lower()
        has_except = "except" in u or "accept" in u or "but not" in u or "keep" in u

        if has_except:
            for splitter in ["except", "accept", "but not", "keep"]:
                if splitter in u:
                    except_part = u.split(splitter)[-1].strip()
                    break
            # Tab command mein except ka matlab specific browser
            if "firefox" in except_part:
                speak("Closing Chrome tabs only, keeping Firefox, sir.")
                close_all_tabs()
            elif "chrome" in except_part:
                speak("Chrome is the only browser I manage tabs for, sir.")
            else:
                close_all_tabs()
        else:
            close_all_tabs()

        state.touch()
        continue

    # CLOSE ALL APPS - except VS Code aur terminal
    if "close all app" in user_input.lower():
        u = user_input.lower()
        
        # "accept" bhi sun lo kyunki speech recognition "except" ko "accept" sunta hai
        has_except = "except" in u or "accept" in u or "but not" in u or "keep" in u
        
        if has_except:
            # jo bhi word use hua ho usse split karo
            for splitter in ["except", "accept", "but not", "keep"]:
                if splitter in u:
                    except_part = u.split(splitter)[-1].strip()
                    break
            # "and" se split karo multiple apps ke liye
            keep_apps = [
                app.strip() 
                for app in except_part.replace(" and ", ",").split(",")
                if app.strip()
            ]
            close_specific_apps(keep_apps)
        else:
            close_all_apps()
        
        state.touch()
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

    # Add user message to history
    MAX_HISTORY = 10
    conversation.append({"role": "user", "content": user_input})

    # Sirf last 10 messages rakho, system prompt hamesha rakho
    if len(conversation) > MAX_HISTORY + 1:
        conversation = [conversation[0]] + conversation[-(MAX_HISTORY):]
    

    # AI INTENT DETECTION - Natural language samjhe
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
You are an intent extraction engine for a voice assistant named FRIDAY who is female.

Extract the user's intent and return ONLY valid JSON.

ACTIONS:
- "open" → user wants to open app/website
- "close_tab" → close current tab (any variation)
- "close_window" → close current window or specific app
- "close_all_tabs" → close all browser tabs
- "close_all_apps" → close all running apps
- "search" → search something online
- "none" → normal conversation

INTENT EXAMPLES - understand meaning, not exact words:
IMPORTANT: Single words like "explain", "summarize", "read", "write", "search" alone without a clear target → {"action": "none", "target": null}
Only detect "open" action when user clearly wants to open something specific.
"instagram kholna" → {"action": "open", "target": "instagram"}
"instagram kholo" → {"action": "open", "target": "instagram"}
"instagram kholna hai" → {"action": "open", "target": "instagram"}
"mujhe instagram chahiye" → {"action": "open", "target": "instagram"}
"is tab ko band karo" → {"action": "close_tab", "target": null}
"yeh tab band karo" → {"action": "close_tab", "target": null}
"yah tab" → {"action": "close_tab", "target": null}
"tab band karo" → {"action": "close_tab", "target": null}
"band kar do" → {"action": "close_tab", "target": null}
"make screen professional" → {"action": "make_professional", "target": null}
"screen professional" → {"action": "make_professional", "target": null}
"make screen profession" → {"action": "make_professional", "target": null}
"professional screen" → {"action": "make_professional", "target": null}
"instagram band karo" → {"action": "close_window", "target": "instagram"}
"sare tab band karo" → {"action": "close_all_tabs", "target": null}
"sab kuch band karo" → {"action": "close_all_apps", "target": null}
"close all apps except calculator" → {"action": "close_all_apps", "target": "calculator"}
"search weather" → {"action": "search", "target": "weather"}
"weather search karo" → {"action": "search", "target": "weather"}
"kya hal hai" → {"action": "none", "target": null}

ONLY return JSON. Nothing else.
"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    reply = response.choices[0].message.content.strip()
    reply = reply.replace("```json", "").replace("```", "").strip()
    start = reply.find("{")
    end = reply.rfind("}") + 1
    if start != -1 and end != 0:
        reply = reply[start:end]

    try:
        data = json.loads(reply)
        action = data.get("action")
        target = data.get("target")

        if action == "open" and target:
            target = target.lower().strip()

            # Browser apps
            if target in BROWSER_APPS:
                browser_path = BROWSER_APPS[target]
                if os.path.exists(browser_path):
                    os.startfile(browser_path)
                else:
                    os.system(f"start {target}")
                speak(f"Opening {target}, sir.")
                state.touch()
                continue

            # App first, then website
            if target in APP_FIRST:
                app_cmd = APP_FIRST[target]["app"]
                web_url = APP_FIRST[target]["web"]
                try:
                    result = os.system(app_cmd)
                    if result != 0:
                        webbrowser.open(web_url)
                        speak(f"App nahi mili, opening {target} in browser, sir.")
                    else:
                        speak(f"Opening {target}, sir.")
                except:
                    webbrowser.open(web_url)
                    speak(f"Opening {target} in browser, sir.")
                state.touch()
                continue

            # Web apps
            if target in WEB_APPS:
                webbrowser.open(WEB_APPS[target])
                speak(f"Opening {target}, sir.")
                state.touch()
                continue

            # System apps
            if target in SYSTEM_APPS:
                os.system(SYSTEM_APPS[target])
                speak(f"Opening {target}, sir.")
                state.touch()
                continue

            # File dhundho — but sirf agar target clearly file jaisa lage
            # Short words jaise "chrome", "spotify" ke liye file search mat karo
            common_apps = {"chrome", "firefox", "edge", "brave", "spotify", 
                          "discord", "telegram", "whatsapp", "instagram",
                          "notepad", "calculator", "paint", "zoom", "vlc"}
            
            if target not in common_apps:
                file_path = find_file(target)
                if file_path:
                    os.startfile(file_path)
                    speak(f"Opening {target}, sir.")
                    state.touch()
                    continue

            app_path = find_app(target)
            if app_path:
                os.startfile(app_path)
                speak(f"Opening {target}, sir.")
                state.touch()
                continue

            # Last fallback
            os.system(f"start {target}")
            speak(f"Trying to open {target}, sir.")
            state.touch()
            continue

        elif action == "close_tab":
            close_current_tab()
            state.touch()
            continue

        elif action == "close_window":
            if target:
                import psutil
                import subprocess
                target_lower = target.lower()

                # Normal process apps
                PROCESS_APPS = {
                    "spotify": ["spotify.exe"],
                    "chrome": ["chrome.exe"],
                    "firefox": ["firefox.exe"],
                    "telegram": ["telegram.exe"],
                    "discord": ["discord.exe"],
                    "vlc": ["vlc.exe"],
                    "zoom": ["zoom.exe"],
                    "edge": ["msedge.exe"],
                    "brave": ["brave.exe"],
                    "notepad": ["notepad.exe"],
                    "calculator": ["calc.exe", "calculatorapp.exe"],
                }

                # Windows Store apps — PowerShell se band karo by window title
                STORE_APPS = {
                    "instagram": "Instagram",
                    "whatsapp": "WhatsApp",
                    "linkedin": "LinkedIn",
                    "snapchat": "Snapchat",
                    "twitter": "Twitter",
                }

                killed = False

                # Pehle normal process check karo
                if target_lower in PROCESS_APPS:
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            proc_name = proc.info['name'].lower()
                            if any(
                                p.lower() in proc_name
                                for p in PROCESS_APPS[target_lower]
                            ):
                                proc.kill()
                                killed = True
                        except:
                            continue

                # Store apps — window title se band karo
                elif target_lower in STORE_APPS:
                    window_title = STORE_APPS[target_lower]
                    try:
                        result = subprocess.run(
                            ['powershell', '-command',
                             f'Get-Process | Where-Object {{$_.MainWindowTitle -like "*{window_title}*"}} | Stop-Process -Force'],
                            capture_output=True, text=True, timeout=5
                        )
                        killed = True
                    except Exception as e:
                        print(f"Store app close error: {e}")

                if killed:
                    speak(f"{target}closed , boss.")
                else:
                    speak(f"{target} chal nahi rahi thi boss.")
            else:
                close_current_window()

            state.touch()
            continue

        elif action == "close_all_tabs":
            close_all_tabs()
            state.touch()
            continue
        
        elif action == "make_professional":
            screen_text = read_screen()
            if not screen_text:
                speak("Screen pe kuch readable nahi mila boss.")
                state.touch()
                continue

            prof_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": """
Rewrite the given text in a professional tone.
STRICT RULES:
- Rewrite ONLY the actual content — ignore any file names, menu items, or UI text.
- Do NOT mention title bars, menus, file names, or anything technical.
- Do NOT add any intro like "Here is..." or "The following..."
- Output ONLY the clean professionally rewritten text.
"""
                    },
                    {
                        "role": "user",
                        "content": f"Rewrite professionally:\n\n{screen_text}"
                    }
                ]
            )

            reply = prof_response.choices[0].message.content
            print("FRIDAY:", reply)
            speak("Done boss, pasting the professional version.")

            import pygetwindow as gw
            notepad_windows = [
                w for w in gw.getAllWindows()
                if 'notepad' in w.title.lower() or '.txt' in w.title.lower()
            ]

            if notepad_windows:
                notepad_windows[0].activate()
                time.sleep(0.8)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                pyperclip.copy(reply)
                pyautogui.hotkey('ctrl', 'v')
                speak("Notepad updated, boss.")
            else:
                pyperclip.copy(reply)
                speak("Copied to clipboard boss, Ctrl V se paste kar lo.")

            state.touch()
            continue

        elif action == "close_all_apps":
            if target:
                # Multiple apps "spotify and discord" handle karo
                keep_apps = [
                    app.strip()
                    for app in target.replace(" and ", ",").replace(" or ", ",").split(",")
                    if app.strip()
                ]
                close_specific_apps(keep_apps)
            else:
                close_all_apps()
            state.touch()
            continue

        elif action == "search" and target:
            url = f"https://www.google.com/search?q={target}"
            webbrowser.open(url)
            speak(f"Searching for {target}, sir.")
            state.touch()
            continue

        elif action == "none" or not action:
            # Normal AI conversation
            normal_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"""
You are FRIDAY, a smart female AI assistant — calm, confident, and precise.

User's saved memory:
{json.dumps(memory, indent=2)}

TONE RULES — very important:
TONE RULES — very important:
- You are FRIDAY, a smart female AI assistant.
- Never say "main aapki madad kar sakta hoon" — you are female, say "kar sakti hoon" if needed.
- Keep responses short — 1 to 2 sentences max.
- Address user as "boss".
- If you don't understand, say: "Samajh nahi aaya boss, thoda clear karo."
- NEVER give long multi-sentence Hindi explanations for simple unclear inputs.
- If input is just one unclear word, say exactly: "Kya matlab hai boss, thoda clear karo."
- Maximum 1-2 sentences in any response.
- Do not make up information from memory unprompted.
- Only use memory when user specifically asks about themselves.

LANGUAGE RULES — most important:
- Do NOT just copy the user's language blindly.
- Think about what sounds most NATURAL for that specific reply.
- Simple factual answers like time, date, weather → short English is fine even if asked in Hindi.
  Example: "time kya hua hai" → "It's 3:39 PM, boss." ✅
  Not: "Abhi 3 baj ke 39 minute hue hain PM boss." ❌
- Emotional or casual chat → match user's vibe.
  Example: "kya hal hai" → "Sab theek boss, aap batao?" ✅
- If user speaks pure Hindi → reply in simple clean Hindi.
- If user speaks pure English → reply in English.
- If user speaks Hinglish → reply naturally in Hinglish.
- NEVER mix grammar awkwardly. Natural > Consistent.

MEMORY RULES:
- Use saved memory to answer personal questions directly.
- If answer is in memory, answer confidently.
- If not in memory, say "Woh info abhi mere paas nahi hai boss."

EXAMPLES of good responses:
User: kya hal hai → FRIDAY: Sab theek hai boss, aap batao?
User: mera naam kya hai → FRIDAY: Aapka naam Harsh hai boss.
User: what time is it → FRIDAY: Let me check that for you, boss.
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

    except Exception as e:
        print("Intent error:", e)

