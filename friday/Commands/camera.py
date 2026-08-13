"""
Camera Feed — webcam se real-time visual input.
Gemini Vision se analyze karo.
"""

import os
import base64
import threading
import cv2
from dotenv import load_dotenv
from friday.voice import speak

load_dotenv()

_camera_active = False
_cap = None


def capture_frame() -> str | None:
    """Webcam se ek frame capture karo aur base64 return karo."""
    global _cap

    try:
        if _cap is None or not _cap.isOpened():
            # DirectShow backend use karo Windows pe
            _cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            if not _cap.isOpened():
                # Fallback — other indices
                for idx in range(1, 4):
                    _cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                    if _cap.isOpened():
                        print(f"✅ Camera found at index {idx}")
                        break

        if not _cap.isOpened():
            print("❌ Camera not found")
            return None

        ret, frame = _cap.read()
        if not ret:
            return None

        _, buffer = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(buffer).decode('utf-8')
        return b64

    except Exception as e:
        print(f"Camera capture error: {e}")
        return None


def analyze_frame(prompt: str = "What do you see?") -> str:
    """Frame capture karo aur Groq Vision se analyze karo."""
    import base64
    from groq import Groq
    import os

    b64_frame = capture_frame()
    if not b64_frame:
        return "Camera not available, boss."

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_frame}"
                            }
                        },
                        {
                            "type": "text",
                            "text": f"{prompt} Keep response under 3 sentences. No markdown."
                        }
                    ]
                }
            ],
            max_tokens=150,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Vision error: {e}")
        return "Couldn't analyze the image, boss."
    
    
def release_camera():
    """Camera release karo."""
    global _cap
    if _cap and _cap.isOpened():
        _cap.release()
        _cap = None


def handle_camera_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    camera_triggers = [
        "camera dekho", "camera se dekho",
        "yeh kya hai", "ye kya hai",
        "kya dikh raha hai", "camera on",
        "webcam se dekho", "camera",
        "what do you see", "look at this",
        "dekho yeh", "identify this",
        "camera se batao", "photo lo aur batao",
    ]

    if not any(t in u for t in camera_triggers):
        return False

    # Prompt extract karo
    prompt_map = {
        "yeh kya hai": "What is this object? Identify it clearly.",
        "ye kya hai": "What is this object? Identify it clearly.",
        "kya dikh raha hai": "Describe everything you see in detail.",
        "what do you see": "Describe what you see.",
        "identify this": "Identify what this is.",
        "look at this": "What is this?",
        "dekho yeh": "What is this?",
    }

    prompt = "What do you see in front of the camera? Describe briefly."
    for key, val in prompt_map.items():
        if key in u:
            prompt = val
            break

    # Custom prompt agar user ne kuch specific kaha
    custom_triggers = [
        "camera se batao", "camera dekho",
        "webcam se dekho", "camera se dekho",
        "camera dekhna",
    ]
    for t in custom_triggers:
        if t in u:
            remaining = u.replace(t, "").strip()
            if remaining and len(remaining) > 3:
                prompt = remaining
            break

    speak("Looking, give me a second boss.")

    def _analyze():
        result = analyze_frame(prompt)
        print(f"👁️ Camera: {result}")
        speak(result)
        release_camera()

    threading.Thread(target=_analyze, daemon=True).start()
    return True