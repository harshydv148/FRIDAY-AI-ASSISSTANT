"""
Clipboard History — copied text track karna.
"""

import time
import threading
import pyperclip
from friday.voice import speak

MAX_HISTORY = 10
_clipboard_history = []
_last_copied = ""
_monitoring = False


def start_monitoring():
    """Background mein clipboard monitor karo."""
    global _monitoring
    if _monitoring:
        return
    _monitoring = True
    thread = threading.Thread(target=_monitor_loop, daemon=True)
    thread.start()
    print("📋 Clipboard monitoring started.")


def _monitor_loop():
    """Har 1 second mein clipboard check karo."""
    global _last_copied, _clipboard_history

    while _monitoring:
        try:
            current = pyperclip.paste()
            if current and current != _last_copied:
                _last_copied = current
                # Filter karo — code, short strings, friday output
                skip_patterns = [
                    "FRIDAY:", "You:", "🎤", "📋", "🌐",
                    "def ", "import ", "class ", "return ",
                    '"""', "```",
                ]
                should_skip = any(p in current for p in skip_patterns)
                
                if not should_skip and len(current) > 5 and current not in _clipboard_history:
                    _clipboard_history.append(current)
                    print(f"📋 Clipboard saved: {current[:50]}")
                    # Max limit
                    if len(_clipboard_history) > MAX_HISTORY:
                        _clipboard_history.pop(0)
                    print(f"📋 Clipboard saved: {current[:50]}...")
        except:
            pass
        time.sleep(1)


def show_history():
    """Clipboard history dikhao."""
    if not _clipboard_history:
        speak("Clipboard is empty, boss.")
        return

    print("\n📋 Clipboard History:")
    for i, item in enumerate(_clipboard_history[-5:], 1):
        preview = item[:50] + "..." if len(item) > 50 else item
        print(f"  [{i}] {preview}")

    speak(f"{len(_clipboard_history)} items in clipboard history, boss. Check terminal.")


def paste_item(index: int):
    """Specific clipboard item clipboard mein copy karo."""
    if not _clipboard_history:
        speak("Clipboard is empty, boss.")
        return

    idx = index - 1
    if idx < 0 or idx >= len(_clipboard_history):
        speak(f"No item {index} in clipboard, boss.")
        return

    item = _clipboard_history[idx]
    pyperclip.copy(item)
    speak(f"Item {index} copied to clipboard boss, press Ctrl V wherever you want.")
    print(f"📋 Ready to paste: {item[:50]}")


def clear_history():
    """Clipboard history clear karo."""
    global _clipboard_history
    _clipboard_history.clear()
    speak("Clipboard history cleared, boss.")


def handle_clipboard_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    import re

    # Pehle number check karo — "clipboard 2"
    paste_match = re.search(r'clipboard\s+(\d+)', u)
    if paste_match:
        index = int(paste_match.group(1))
        paste_item(index)
        return True

    # Clear
    if any(t in u for t in [
        "clear clipboard", "clipboard clear",
        "clipboard history clear",
    ]):
        clear_history()
        return True

    # Show history — last mein check karo
    if any(t in u for t in [
        "clipboard", "clipboard dikhao", "clipboard history",
        "what did i copy", "copied items", "clipboard list",
        "show clipboard", "clipboard check",
    ]):
        show_history()
        return True

    return False