"""
Music Control — YouTube Music via browser.
Spotify local control via keyboard shortcuts.
"""

import os
import re
import webbrowser
import pyautogui
import time
from friday.voice import speak


def play_song(query: str):
    """yt-dlp se song dhundho, browser mein directly open karo."""
    import subprocess
    import webbrowser
    import threading

    def _find_and_play():
        try:
            speak(f"Finding {query}, boss.")
            
            # yt-dlp se pehla result ka URL lo
            result = subprocess.run(
                [
                    "yt-dlp",
                    f"ytsearch1:{query}",
                    "--get-url",
                    "--no-playlist",
                    "-f", "best",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            
            url = result.stdout.strip().split('\n')[0]
            
            if not url:
                # Fallback — YouTube Music search
                encoded = query.replace(" ", "+")
                webbrowser.open(
                    f"https://music.youtube.com/search?q={encoded}"
                )
                speak(f"Opened YouTube Music for {query}, boss.")
                return

            # Direct YouTube video URL browser mein kholo
            # yt-dlp stream URL se video ID nikalo
            video_id_result = subprocess.run(
                [
                    "yt-dlp",
                    f"ytsearch1:{query}",
                    "--get-id",
                    "--no-playlist",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            video_id = video_id_result.stdout.strip().split('\n')[0]

            if video_id:
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(youtube_url)
                speak(f"Playing {query}, boss.")
                print(f"🎵 YouTube: {youtube_url}")
            else:
                encoded = query.replace(" ", "+")
                webbrowser.open(
                    f"https://music.youtube.com/search?q={encoded}"
                )
                speak(f"Opened YouTube Music, boss.")

        except Exception as e:
            print(f"Music error: {e}")
            encoded = query.replace(" ", "+")
            webbrowser.open(
                f"https://music.youtube.com/search?q={encoded}"
            )
            speak(f"Opened YouTube Music for {query}, boss.")

    threading.Thread(target=_find_and_play, daemon=True).start()

def play_pause():
    """Space key se play/pause toggle karo."""
    try:
        pyautogui.press('space')
        speak("Done, boss.")
    except Exception as e:
        speak("Couldn't control music, boss.")


def next_track():
    """Next track — Shift+N (YouTube Music shortcut)."""
    try:
        pyautogui.hotkey('shift', 'n')
        speak("Next track, boss.")
    except Exception as e:
        speak("Couldn't skip, boss.")


def previous_track():
    """Previous track — Shift+P (YouTube Music shortcut)."""
    try:
        pyautogui.hotkey('shift', 'p')
        speak("Previous track, boss.")
    except Exception as e:
        speak("Couldn't go back, boss.")


def handle_spotify_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    # Play specific song
    play_triggers = [
        "play ", "chalao ", "gaana chalao",
        "song play karo", "music play karo",
        "play song", "bajao ", "search song",
        "youtube music", "gaana dhundho",
    ]
    for trigger in play_triggers:
        if trigger in u:
            query = u
            for t in play_triggers:
                query = query.replace(t, "").strip()
            query = query.replace("friday", "").strip()
            if query and len(query) > 2:
                play_song(query)
                return True

    # Pause/Play toggle
    if any(t in u for t in [
        "pause", "stop music", "music band karo",
        "music rok", "gaana rok", "pause karo",
        "music pause",
    ]):
        play_pause()
        return True

    if any(t in u for t in [
        "resume music", "music chalu", "gaana chalu",
        "music resume", "music on", "unpause",
    ]):
        play_pause()
        return True

    # Next track
    if any(t in u for t in [
        "next song", "next track", "agla gaana",
        "skip song", "next gaana", "agle gaane pe jao",
    ]):
        next_track()
        return True

    # Previous track
    if any(t in u for t in [
        "previous song", "previous track", "pichla gaana",
        "back song", "pehle wala gaana",
    ]):
        previous_track()
        return True

    return False