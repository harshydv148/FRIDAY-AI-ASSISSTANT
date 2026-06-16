"""
Face Authentication — mediapipe se Harsh ko identify karna.
"""

import os
import json
import numpy as np
import cv2
import mediapipe as mp
from friday.voice import speak

FACE_DATA_FILE = "friday_face_data.json"

mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh


def _get_face_landmarks(frame) -> list | None:
    """Frame se face landmarks extract karo."""
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0]
        points = []
        for lm in landmarks.landmark:
            points.append([lm.x, lm.y, lm.z])

        return points


def _landmarks_to_vector(landmarks: list) -> np.ndarray:
    """Landmarks ko normalized vector mein convert karo."""
    arr = np.array(landmarks).flatten()
    # Normalize karo
    arr = (arr - arr.mean()) / (arr.std() + 1e-6)
    return arr


def register_face() -> bool:
    """Harsh ka face register karo."""
    from friday.Commands.camera import capture_frame
    import base64

    speak("Look at the camera boss, registering your face.")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Camera not found, boss.")
        return False

    samples = []
    attempts = 0

    while len(samples) < 5 and attempts < 30:
        ret, frame = cap.read()
        if not ret:
            attempts += 1
            continue

        landmarks = _get_face_landmarks(frame)
        if landmarks:
            vector = _landmarks_to_vector(landmarks)
            samples.append(vector.tolist())
            print(f"📸 Captured sample {len(samples)}/5")

        attempts += 1

    cap.release()

    if len(samples) < 3:
        speak("Couldn't capture your face properly, boss. Try again with better lighting.")
        return False

    # Average vector save karo
    avg_vector = np.mean(samples, axis=0).tolist()

    with open(FACE_DATA_FILE, "w") as f:
        json.dump({"boss_face": avg_vector}, f)

    speak("Face registered, boss. I'll recognize you now.")
    print("✅ Face registered successfully.")
    return True


def verify_face() -> str:
    """
    Current face check karo — boss hai ya nahi.
    Returns: "boss", "unknown", "no_face"
    """
    if not os.path.exists(FACE_DATA_FILE):
        return "not_registered"

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "no_camera"

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "no_face"

    landmarks = _get_face_landmarks(frame)
    if not landmarks:
        return "no_face"

    current_vector = _landmarks_to_vector(landmarks)

    with open(FACE_DATA_FILE, "r") as f:
        data = json.load(f)

    boss_vector = np.array(data["boss_face"])

    # Cosine similarity
    similarity = np.dot(current_vector, boss_vector) / (
        np.linalg.norm(current_vector) * np.linalg.norm(boss_vector) + 1e-6
    )

    print(f"🔍 Face similarity: {similarity:.3f}")

    # Threshold — adjust based on testing
    if similarity > 0.97:
        return "boss"
    else:
        return "unknown"


def handle_face_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    if any(t in u for t in [
        "register my face", "register face",
        "remember my face", "face register karo",
        "save my face", "learn my face",
    ]):
        register_face()
        return True

    if any(t in u for t in [
        "who am i", "verify face", "check face",
        "am i boss", "face check karo",
        "kaun hu main",
    ]):
        result = verify_face()
        if result == "boss":
            speak("You're Harsh, my boss.")
        elif result == "unknown":
            speak("I don't recognize you. You're not registered as boss.")
        elif result == "not_registered":
            speak("I don't have a registered face yet, boss. Say 'register my face'.")
        elif result == "no_face":
            speak("I can't see a face, boss.")
        else:
            speak("Camera not available, boss.")
        return True

    return False        

import datetime

INTRUDER_LOG_FILE = "friday_intruder_log.json"


def log_intruder():
    """Unknown user ka log save karo."""
    try:
        logs = []
        if os.path.exists(INTRUDER_LOG_FILE):
            with open(INTRUDER_LOG_FILE, "r") as f:
                logs = json.load(f)

        entry = {
            "time": datetime.datetime.now().strftime("%d %b %Y %H:%M:%S"),
        }
        logs.append(entry)

        with open(INTRUDER_LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)

        print(f"⚠️ Intruder logged: {entry['time']}")
    except Exception as e:
        print(f"Log error: {e}")


def get_intruder_report() -> str:
    """Intruder log padhkar report banao."""
    if not os.path.exists(INTRUDER_LOG_FILE):
        return None

    try:
        with open(INTRUDER_LOG_FILE, "r") as f:
            logs = json.load(f)

        if not logs:
            return None

        return logs

    except:
        return None


def clear_intruder_log():
    """Intruder log clear karo."""
    if os.path.exists(INTRUDER_LOG_FILE):
        with open(INTRUDER_LOG_FILE, "w") as f:
            json.dump([], f)