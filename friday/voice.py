from groq import Groq
from gtts import gTTS
import pygame
import pytesseract
import mss
import os
import time
import speech_recognition as sr
import uuid

pygame.mixer.init()

def speak(text):
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
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


def should_speak(text):
    # Code blocks mat bolo
    if "```" in text:
        return False
    # Pure code detect karo
    code_lines = sum(
        1
        for line in text.split("\n")
        if line.strip().startswith(
            ("def ", "class ", "import ", "for ", "if ", "while ", "#")
        )
    )
    if code_lines > 3:
        return False
    # Bohot lamba text truncate karke bolo
    return True

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