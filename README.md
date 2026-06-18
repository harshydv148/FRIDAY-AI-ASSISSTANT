# F.R.I.D.A.Y. 🤖

> *"Fully Responsive Intelligent Digital Assistant for You"*

A Tony Stark-inspired personal AI voice assistant built with Python — modular, offline-capable, and genuinely smart.

Ever since watching Iron Man, I wanted my own FRIDAY — just like Tony Stark's AI assistant. This project is my attempt at building that dream, one feature at a time.

> *"Sometimes you gotta run before you can walk."* — Tony Stark

Built by **Harsh Yadav**, a BCA student from Haryana — using AI tools, step by step, entirely from his own ideas. This project demonstrates how a non-programmer can build production-quality software through AI collaboration.

---

## 📸 Preview

```
FRIDAY online
✅ Piper Amy loaded — voice ready.
🎤 Listening...

You: friday open instagram
FRIDAY: Opening instagram, boss.

You: summarise screen
FRIDAY: Boss, this appears to be a LeetCode problem about...

You: help me solve this
🎓 GUIDE MODE: This is a classic DFS problem boss...

You: latest news kya hai
🔍 Searching: top world news headlines today...
FRIDAY: Here are the top stories boss — ...
```

---

## ✨ Features

### 🎙️ Voice & AI
- Wake word detection — say **"Friday"** to activate
- Natural language understanding — Hindi, English, Hinglish
- Smart memory — remembers your personal info across sessions
- Conversation history — picks up where you left off
- ADA-inspired personality — witty, confident, natural
- Self-aware — knows her own codebase and features
- Standby mode — auto and manual both

### 🖥️ System Control
- Open & close apps/websites by voice
- Volume control — up, down, mute, unmute, set exact level
- Lock screen, shutdown, restart
- Close all apps (with process protection — won't close itself)
- Screenshot capture with auto-save to Desktop
- Network speed check

### 📋 Productivity
- Smart Notes with reminders — popup + voice alert even in standby
- To-Do list management — add, complete, delete tasks
- Timer, Alarm, Stopwatch (floating window)
- Clipboard history — track & paste copied items by index
- Study mode — opens all study sites at once

### 🌐 Web & Information
- Real-time search — live news, scores, prices (DuckDuckGo)
- Weather with rain detection (OpenWeatherMap)
- YouTube Music direct play (yt-dlp — no browser needed)
- Music controls — pause, next, previous

### 💻 Developer Tools
- Git commands — status, add, commit, push, pull, branch, checkout
- OCR screen reading — explain, summarize, rewrite professionally
- LeetCode guide mode — Socratic teaching, hints, pattern recognition
- Direct solve mode — complete solution pasted at cursor
- Type command — AI generates content and pastes it anywhere
- Camera feed — webcam + Groq Vision for object identification

### 🔍 Smart Search
- Real-time web search via DuckDuckGo (no API key needed)
- Live news headlines
- Stock/crypto prices
- Sports scores
- Any current information

---

## 🏗️ Architecture

```
friday-tony-stark-demo/
├── cli_friday.py              # Main loop — entry point
│
└── friday/
    ├── AI/
    │   ├── intent.py          # Natural language intent detection (Groq)
    │   └── chat.py            # Conversational AI (Groq llama-3.3-70b)
    │
    ├── Automation/
    │   ├── apps.py            # App open/close, process management
    │   ├── browser.py         # Browser & tab control
    │   ├── system.py          # Shutdown, restart, lock
    │   └── volume.py          # Volume control (PowerShell)
    │
    ├── Commands/
    │   ├── screen.py          # OCR screen reading, explain, solve, guide
    │   ├── files.py           # File search, type command
    │   ├── shortcuts.py       # Time, date, standby, study mode
    │   ├── screenshot.py      # Screenshot capture
    │   ├── timer.py           # Timer, alarm, stopwatch
    │   ├── notes.py           # Smart notes + reminders
    │   ├── todo.py            # To-do list
    │   ├── weather.py         # Weather (OpenWeatherMap)
    │   ├── spotify.py         # YouTube Music control
    │   ├── git_commands.py    # Git operations
    │   ├── network.py         # Network speed check
    │   ├── clipboard.py       # Clipboard history
    │   ├── camera.py          # Webcam + Groq Vision
    │   └── search.py          # Real-time web search
    │
    ├── Personality/
    │   ├── prompts.py         # All system prompts
    │   └── self_knowledge.py  # Friday reads her own codebase
    │
    ├── app_config.py          # App & website configurations
    ├── memory.py              # Persistent memory + conversation history
    ├── voice.py               # Piper TTS + Google STT
    └── state.py               # Wake/standby state management
```

---

## ⚡ Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| **STT** | Google Speech Recognition | Free |
| **LLM** | Groq — llama-3.3-70b-versatile | Free tier |
| **TTS** | Piper Amy (offline) | Free forever |
| **Vision** | Groq Vision — llama-4-scout | Free tier |
| **Search** | DuckDuckGo | Free, no API key |
| **Weather** | OpenWeatherMap API | Free tier |
| **Music** | yt-dlp + YouTube | Free |
| **Package Manager** | uv | Free |

> **Total running cost: $0** — entirely free stack.

---

## 🚀 Quick Start

### 1. Prerequisites

- Python ≥ 3.11
- [`uv`](https://github.com/astral-sh/uv) — `pip install uv`
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — for screen reading
- [FFmpeg](https://ffmpeg.org/) — for music playback (`winget install ffmpeg`)

### 2. Clone & Install

```bash
git clone https://github.com/harshydv148/FRIDAY-AI-ASSISSTANT.git
cd FRIDAY-AI-ASSISSTANT
uv sync
```

### 3. Set up Environment

```bash
cp .env.example .env
```

Fill in your API keys:

| Variable | Required | Where to get |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ | [console.groq.com](https://console.groq.com) — free |
| `WEATHER_API_KEY` | optional | [openweathermap.org](https://openweathermap.org/api) — free |
| `WEATHER_CITY` | optional | Your city name (e.g. `Rewari`) |
| `GOOGLE_API_KEY` | optional | [aistudio.google.com](https://aistudio.google.com) — for camera vision |

### 4. Download Piper Voice Model

```bash
python -c "
import requests, os
os.makedirs('piper_models', exist_ok=True)
base = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/'
for f in ['en_US-amy-medium.onnx', 'en_US-amy-medium.onnx.json']:
    print(f'Downloading {f}...')
    r = requests.get(base + f)
    open(f'piper_models/{f}', 'wb').write(r.content)
print('Done!')
"
```

### 5. Run

```bash
python cli_friday.py
```

Say **"Friday"** to wake her up! 🎤

---

## 🎤 Voice Commands

### Basic
```
friday                          → wake up
friday open chrome              → open Chrome
friday close all apps           → close everything
exit                            → shut down Friday
```

### System
```
volume up / volume down
volume 50 karo
mute / unmute
screenshot lo
lock screen
network speed check
```

### Productivity
```
note karo meeting hai kal 5 baje    → smart reminder at 5 PM
show notes
add task DSA practice karna hai
todo list
complete DSA
timer 25 minutes
stopwatch start
pomodoro
clipboard dikhao
clipboard 2
```

### Screen & AI
```
explain screen
summarise screen
make screen professional
help me solve this              → LeetCode guide mode (Socratic)
solve screen                    → direct solution pasted
type merge sort                 → AI generates + pastes code
```

### Music
```
play shape of you
pause / resume
next song
previous song
```

### Search & Info
```
latest news kya hai
Bitcoin price abhi
IPL score kya hai
weather kya hai
will it rain
```

### Git
```
git status
commit karo fix login bug
git push
git pull
current branch
new branch feature-auth
```

### Memory
```
I like biryani                  → auto-saved
my name is Harsh                → auto-saved
what's my favourite food        → recalled from memory
```

---

## 🧠 How Memory Works

Friday remembers two types of information:

**Personal Facts** — auto-saved when you mention them:
```
"I like biryani"      → saves favourite_food = biryani
"I am 20 years old"   → saves age = 20
"my city is Delhi"    → saves city = Delhi
```

**Conversation History** — last 20 conversations saved across sessions.
Friday picks up where you left off — even after restart.

---

## ⚠️ Known Limitations

- **WhatsApp automation** — limited without premium API
- **Spotify control** — requires Spotify Premium for playback API
- **Gemini Vision** — free tier quota limited (uses Groq Vision as fallback)
- **Screen reading** — OCR accuracy depends on screen content and font
- **Speech recognition** — requires internet connection (Google STT)
- **Music controls** (pause/next) — requires YouTube to be open in browser

---

## 🔮 Future Plans

- [ ] Web Agent — autonomous browser control (Playwright)
- [ ] GUI interface — PyQt6 dashboard
- [ ] Email integration — read & send emails
- [ ] Google Calendar — schedule management
- [ ] Mobile companion app
- [ ] Multi-language TTS

---

## 📁 Data Files Created

| File | Purpose |
|------|---------|
| `memory.json` | Personal facts + conversation history |
| `friday_notes.json` | Smart notes with reminders |
| `friday_todos.json` | To-do list |
| `piper_models/` | Offline TTS voice model |

---

## 🙏 Inspiration

Ever since watching Iron Man, I wanted my own FRIDAY — just like Tony Stark's AI assistant.
This project is my attempt at building that dream, one feature at a time.

> *"Sometimes you gotta run before you can walk."* — Tony Stark

---

## 📄 License

MIT License — feel free to use, but give credit to Harsh Yadav.

© 2026 Harsh Yadav