"""
App management — open, close, process control.
"""

import os
import subprocess
import webbrowser
import psutil

from friday.voice import speak
from friday.app_config import (
    WEB_APPS, SYSTEM_APPS, BROWSER_APPS,
    APP_FIRST, common_apps, PROTECTED_PROCESS_NAMES,
)
from friday.Commands.files import find_file, find_file_in_folder, find_app


def get_protected_pids() -> set:
    my_pid = os.getpid()
    protected = set()

    try:
        me = psutil.Process(my_pid)
        protected.add(my_pid)

        try:
            p = me.parent()
            while p:
                protected.add(p.pid)
                p = p.parent()
        except:
            pass

        try:
            for c in me.children(recursive=True):
                protected.add(c.pid)
        except:
            pass

    except:
        protected.add(my_pid)

    return protected


def close_all_apps():
    protected_pids = get_protected_pids()
    protected_names = PROTECTED_PROCESS_NAMES

    print(f"🛡️ My PID chain: {protected_pids}")

    closed = []
    skipped = []

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pid = proc.info["pid"]
            name = proc.info["name"].lower()

            if pid in protected_pids:
                skipped.append(f"{name}({pid})")
                continue

            if name in protected_names:
                continue

            proc.kill()
            closed.append(name)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception:
            continue

    print(f"✅ Closed: {list(set(closed))}")
    print(f"🛡️ Skipped (protected): {skipped}")

    if closed:
        speak("All background apps closed, boss.")
    else:
        speak("No apps to close, boss.")


def close_specific_apps(app_names_to_keep: list):
    protected_pids = get_protected_pids()
    protected_names = PROTECTED_PROCESS_NAMES

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

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pid = proc.info["pid"]
            name = proc.info["name"].lower()

            if pid in protected_pids:
                continue

            if name in protected_names:
                continue

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

    kept = ", ".join(app_names_to_keep)
    print(f"✅ Closed all except: {kept}")
    speak(f"Done boss, kept {kept} running.")


def close_specific_window(target: str):
    """Specific app window band karo"""
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

    STORE_APPS = {
        "instagram": "Instagram",
        "whatsapp": "WhatsApp",
        "linkedin": "LinkedIn",
        "snapchat": "Snapchat",
        "twitter": "Twitter",
    }

    target_lower = target.lower()
    killed = False

    if target_lower in PROCESS_APPS:
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                proc_name = proc.info["name"].lower()
                if any(
                    p.lower() in proc_name
                    for p in PROCESS_APPS[target_lower]
                ):
                    proc.kill()
                    killed = True
            except:
                continue

    elif target_lower in STORE_APPS:
        window_title = STORE_APPS[target_lower]
        try:
            subprocess.run(
                [
                    "powershell",
                    "-command",
                    f'Get-Process | Where-Object {{$_.MainWindowTitle -like "*{window_title}*"}} | Stop-Process -Force',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            killed = True
        except Exception as e:
            print(f"Store app close error: {e}")

    if killed:
        speak(f"{target} close ho gayi, boss.")
    else:
        speak(f"{target} chal nahi rahi thi boss.")


def open_app(target: str):
    """App ya website kholna"""

    # 1. Browser
    if target in BROWSER_APPS and BROWSER_APPS[target]:
        if os.path.exists(BROWSER_APPS[target]):
            os.startfile(BROWSER_APPS[target])
        else:
            os.system(f"start {target}")
        speak(f"Opening {target}, boss.")
        return

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
        return

    # 3. Web apps
    if target in WEB_APPS:
        webbrowser.open(WEB_APPS[target])
        speak(f"Opening {target}, boss.")
        return

    # 4. System apps
    if target in SYSTEM_APPS:
        os.system(SYSTEM_APPS[target])
        speak(f"Opening {target}, boss.")
        return

    # 5. File search — common apps ke liye skip
    if target not in common_apps:
        if "from" in target and "folder" in target:
            parts = target.split("from")
            file_name = parts[0].strip()
            folder_name = parts[1].replace("folder", "").strip()
            file_path = find_file_in_folder(folder_name, file_name)
            if file_path:
                os.startfile(file_path)
                speak(f"Opening {file_name}, boss.")
                return

        file_path = find_file(target)
        if file_path:
            os.startfile(file_path)
            speak(f"Opening {target}, boss.")
            return

    # 6. Start menu se dhundho
    app_path = find_app(target)
    if app_path:
        os.startfile(app_path)
        speak(f"Opening {target}, boss.")
        return

    # 7. Last fallback
    os.system(f"start {target}")
    speak(f"Trying to open {target}, boss.")


def handle_open_command(user_input: str) -> bool:
    """
    Open command handle karo.
    Returns True agar handle hua.
    """
    if not user_input.lower().startswith("open"):
        return False

    target = user_input.lower().replace("open", "").strip()

    if not target:
        speak("Kya kholna hai boss?")
        return True

    # Special OS folders
    if "downloads" in target:
        os.startfile(os.path.expanduser("~\\Downloads"))
        speak("Opening downloads, boss.")
        return True

    if "desktop" in target:
        os.startfile(os.path.expanduser("~\\Desktop"))
        speak("Opening desktop, boss.")
        return True

    open_app(target)
    return True


def handle_close_apps(user_input: str) -> bool:
    """
    Close all apps command handle karo.
    Returns True agar handle hua.
    """
    u = user_input.lower()

    if "close all app" not in u:
        return False

    has_except = any(
        w in u for w in ["except", "accept", "but not", "keep"]
    )

    if has_except:
        for splitter in ["except", "accept", "but not", "keep"]:
            if splitter in u:
                except_part = u.split(splitter)[-1].strip()
                break

        keep_apps = [
            app.strip()
            for app in except_part
            .replace(" and ", ",")
            .replace(" or ", ",")
            .split(",")
            if app.strip()
        ]
        close_specific_apps(keep_apps)
    else:
        close_all_apps()

    return True