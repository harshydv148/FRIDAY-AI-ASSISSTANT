"""
Voice — STT aur TTS for FRIDAY.
Piper TTS Amy — offline, fast, no credits needed.
Google Speech Recognition for STT.
"""

import os
import time
import uuid
import wave
import tempfile
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

PIPER_MODEL = "piper_models/en_US-amy-medium.onnx"

# Piper voice — ek baar load karo
_piper_voice = None


def _load_piper():
    """Piper model load karo — ek baar."""
    global _piper_voice
    if _piper_voice is None:
        try:
            from piper import PiperVoice
            _piper_voice = PiperVoice.load(PIPER_MODEL)
            print("✅ Piper Amy loaded — voice ready.")
        except Exception as e:
            print(f"⚠️ Piper load error: {e}")


def _init_gemini():
    """Compatibility function — Piper load karo."""
    _load_piper()


def speak(text: str):
    """Piper Amy se text speak karo."""
    print(f"FRIDAY: {text}")

    if _piper_voice is None:
        _load_piper()

    if _piper_voice is None:
        _gtts_speak(text)
        return

    try:
        # Temp WAV file mein save karo
        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as tmp:
            tmp_path = tmp.name

        with wave.open(tmp_path, 'wb') as w:
            _piper_voice.synthesize_wav(text, w)

        # Play karo
        with wave.open(tmp_path) as w:
            frames = w.readframes(w.getnframes())
            rate = w.getframerate()

        audio = np.frombuffer(frames, dtype=np.int16)
        try:
            sd.stop()
        except:
            pass
        time.sleep(0.1)
        sd.play(audio, samplerate=rate)
        sd.wait()
        
        # Cleanup
        os.remove(tmp_path)

    except Exception as e:
        print(f"Piper speak error: {e}")
        _gtts_speak(text)


def _gtts_speak(text: str):
    """Fallback — gTTS."""
    try:
        import pygame
        from gtts import gTTS

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
        print(f"gTTS error: {e}")


def listen() -> str | None:
    """Microphone se voice input lo."""
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


def should_speak(text: str) -> bool:
    """Check karo text speakable hai ya nahi."""
    if "```" in text:
        return False
    code_lines = sum(
        1 for line in text.split('\n')
        if line.strip().startswith((
            'def ', 'class ', 'import ',
            'for ', 'if ', 'while ', '#'
        ))
    )
    if code_lines > 3:
        return False
    return True