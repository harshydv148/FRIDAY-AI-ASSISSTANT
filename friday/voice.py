"""
Voice — STT aur TTS for FRIDAY.
Piper TTS Amy — offline, fast, no credits needed.
Google Speech Recognition for STT.
Interrupt support — user bol sakta hai jab Friday bol rahi ho.
"""

import os
import time
import uuid
import wave
import tempfile
import threading
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from dotenv import load_dotenv
import threading


load_dotenv()

PIPER_MODEL = "piper_models/en_US-amy-medium.onnx"

_piper_voice = None
_mic_disabled = False
_mic_lock = threading.Lock()
_speaking = False
_interrupt_flag = False


def disable_mic():
    global _mic_disabled
    _mic_disabled = True


def enable_mic():
    global _mic_disabled
    _mic_disabled = False


def is_speaking() -> bool:
    return _speaking


def interrupt_speech():
    """Friday ki speech rok do."""
    global _interrupt_flag
    _interrupt_flag = True
    sd.stop()


def _load_piper():
    global _piper_voice
    if _piper_voice is None:
        try:
            from piper import PiperVoice
            _piper_voice = PiperVoice.load(PIPER_MODEL)
            print("✅ Piper Amy loaded — voice ready.")
        except Exception as e:
            print(f"⚠️ Piper load error: {e}")


def _init_gemini():
    _load_piper()


def speak(text: str):
    """Piper Amy se text speak karo — interruptible."""
    global _speaking, _interrupt_flag

    print(f"FRIDAY: {text}")

    if _piper_voice is None:
        _load_piper()

    if _piper_voice is None:
        _gtts_speak(text)
        return

    _interrupt_flag = False
    _speaking = True

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        with wave.open(tmp_path, 'wb') as w:
            _piper_voice.synthesize_wav(text, w)

        with wave.open(tmp_path) as w:
            frames = w.readframes(w.getnframes())
            rate = w.getframerate()

        audio = np.frombuffer(frames, dtype=np.int16)

        try:
            sd.stop()
        except:
            pass

        time.sleep(0.1)

        if not _interrupt_flag:
            sd.play(audio, samplerate=rate)
            sd.wait()

        os.remove(tmp_path)

    except Exception as e:
        print(f"Piper speak error: {e}")
        _gtts_speak(text)
    finally:
        _speaking = False
        _interrupt_flag = False


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


def listen(silent: bool = False) -> str | None:
    """Microphone se voice input lo — interrupt support ke saath."""
    global _interrupt_flag

    if _mic_disabled:
        time.sleep(0.5)
        return None

    try:
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True

        with _mic_lock:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                if not silent:
                    print("🎤 Listening...")
                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    return None

        try:
            text = r.recognize_google(audio)

            # Agar Friday bol rahi thi toh interrupt karo
            if _speaking:
                print("⚡ Interrupted!")
                interrupt_speech()

            return text
        except sr.UnknownValueError:
            if not silent:
                print("Sorry, couldn't understand.")
            return None
        except sr.RequestError:
            print("⚠️ Speech recognition unavailable.")
            return None
        except Exception:
            return None

    except AssertionError:
        time.sleep(0.5)
        return None
    except OSError:
        time.sleep(0.5)
        return None
    except Exception as e:
        print(f"Listen error: {e}")
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