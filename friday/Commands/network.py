"""
Network Speed — internet speed check karna.
"""

from friday.voice import speak, disable_mic, enable_mic


def check_speed():
    """Internet speed check karo."""
    try:
        import speedtest
        print("🌐 Running speed test...")
        st = speedtest.Speedtest()
        st.get_best_server()

        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping

        print(f"📶 Download: {download:.1f} Mbps")
        print(f"📤 Upload: {upload:.1f} Mbps")
        print(f"🏓 Ping: {ping:.0f} ms")

        enable_mic()
        speak(
            f"Download is {download:.1f} Mbps, "
            f"upload is {upload:.1f} Mbps, "
            f"ping is {ping:.0f} milliseconds, boss."
        )

    except Exception as e:
        print(f"Speed test error: {e}")
        speak("Couldn't run speed test, boss.")


def handle_network_command(user_input: str) -> bool:
    u = user_input.lower().strip()

    speed_triggers = [
        "internet speed", "network speed", "speed test",
        "speedtest", "speed check", "internet kitna fast hai",
        "bandwidth", "connection speed", "net speed",
        "speed kya hai", "internet speed check",
    ]

    if not any(t in u for t in speed_triggers):
        return False

    speak("Running speed test, give me a moment boss.")
    import time
    time.sleep(3)  # Speak + echo settle hone do
    disable_mic()
    check_speed()
    enable_mic()
    return True