"""
WhatsApp Bot — Selenium se WhatsApp Web automation.
"""

import re
import time
from friday.voice import speak
from friday.memory import get_memory, load_memory, save_memory


def get_contact_number(name: str) -> str | None:
    memory = get_memory()
    contacts = memory.get("contacts", {})
    if name.lower() in contacts:
        return contacts[name.lower()]
    for contact_name, number in contacts.items():
        if name.lower() in contact_name.lower():
            return number
    return None


def save_contact(name: str, number: str):
    memory = load_memory()
    if "contacts" not in memory:
        memory["contacts"] = {}
    memory["contacts"][name.lower()] = number
    save_memory(memory)
    print(f"📱 Contact saved: {name} → {number}")
    speak(f"Saved {name}'s number, boss.")


def send_whatsapp_message(name: str, message: str) -> bool:
    try:
        import webbrowser
        import urllib.parse

        # Number dhundho
        number = get_contact_number(name)
        
        if number:
            # Number clean karo
            number = number.strip().replace(" ", "").replace("-", "")
            if not number.startswith("+"):
                number = "+91" + number

            # Encoded message
            encoded_msg = urllib.parse.quote(message)
            
            # WhatsApp Web direct URL — chat seedha khulegaa
            url = f"https://web.whatsapp.com/send?phone={number}&text={encoded_msg}"
            
            speak(f"Opening WhatsApp for {name}, boss.")
            webbrowser.open(url)
            
            speak("WhatsApp opened boss, press Send when ready.")
            print(f"✅ WhatsApp opened: {url}")
            return True
        else:
            speak(f"I don't have {name}'s number boss. Save karo pehle — 'save contact {name} number'.")
            return True

    except Exception as e:
        print(f"WhatsApp error: {e}")
        speak("Couldn't open WhatsApp boss.")
        return False


def handle_whatsapp_command(user_input: str) -> bool:
    u = user_input.lower()

    # Contact save karo
    save_triggers = [
        "save contact", "contact save karo",
        "number save karo", "add contact",
        "contact add karo",
    ]
    if any(t in u for t in save_triggers):
        number_match = re.search(r'(\+?[\d\s]{10,13})', user_input)
        if number_match:
            number = number_match.group(1).replace(" ", "")
            name = u
            for t in save_triggers:
                name = name.replace(t, "").strip()
            name = re.sub(r'[\d\+\s]', '', name).strip()
            if name and number:
                save_contact(name, number)
                return True
        speak("Name aur number dono batao boss.")
        return True

    # Message bhejo
    whatsapp_triggers = [
        "whatsapp karo", "whatsapp bhejo",
        "whatsapp message", "message bhejo",
        "ko whatsapp", "ko message karo",
        "send whatsapp", "whatsapp send",
        "whatsapp kar",
    ]

    if not any(t in u for t in whatsapp_triggers):
        return False

    # Name extract karo
    name = None
    message = None

    # Pattern 1: "X ko whatsapp karo Y"
    ko_match = re.search(r'(.+?)\s+ko\s+(?:whatsapp|message)', u)
    if ko_match:
        name = ko_match.group(1).strip()
        for trigger in ["friday", "whatsapp", "message", "bhejo", "karo"]:
            name = name.replace(trigger, "").strip()
        msg_split = re.split(
            r'ko\s+(?:whatsapp|message)\s*(?:karo|bhejo|kar|karna)?',
            u
        )
        if len(msg_split) > 1:
            message = msg_split[-1].strip()

    # Pattern 2: "whatsapp karo X ko Y"
    if not name:
        karo_match = re.search(
            r'(?:whatsapp|message)\s+(?:karo|bhejo|kar)\s+(.+?)\s+ko',
            u
        )
        if karo_match:
            name = karo_match.group(1).strip()

    if not name:
        speak("Kisko message karna hai boss?")
        return True

    if not message or len(message.strip()) < 2:
        speak(f"Kya message bhejun {name} ko boss?")
        return True

    # Thread mein chalao taaki Friday block na ho
    import threading
    send_whatsapp_message(name, message)
    return True