"""
Volume Control — sound levels manage karna.
Uses Windows built-in approach via pycaw new API.
"""

import re
import subprocess
from friday.voice import speak


def get_volume() -> int:
    """Current volume percentage return karo."""
    try:
        from pycaw.pycaw import AudioUtilities
        sessions = AudioUtilities.GetSpeakers()
        volume = sessions.volume
        return int(volume * 100) if volume else 50
    except:
        # Fallback via PowerShell
        result = subprocess.run(
            ['powershell', '-command',
             '[audio]::Volume * 100'],
            capture_output=True, text=True
        )
        try:
            return int(float(result.stdout.strip()))
        except:
            return 50


def set_volume(level: int):
    """Volume set karo 0-100 ke beech via PowerShell."""
    level = max(0, min(100, level))
    # PowerShell se volume set karo — most reliable
    script = f"""
$volume = {level / 100}
$obj = New-Object -ComObject WScript.Shell
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {{
    int f(); int g(); int h(); int i();
    int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext);
    int j();
    int GetMasterVolumeLevelScalar(out float pfLevel);
    int k(); int l(); int m(); int n();
    int SetMute([MarshalAs(UnmanagedType.Bool)] bool bMute, System.Guid pguidEventContext);
    int GetMute(out bool pbMute);
}}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {{
    int Activate(ref System.Guid id, uint clsCtx, int activationParams, out IAudioEndpointVolume aev);
}}
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {{
    int f();
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
}}
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumeratorComObject {{ }}
public class Audio {{
    static IAudioEndpointVolume Vol() {{
        var enumerator = new MMDeviceEnumeratorComObject() as IMMDeviceEnumerator;
        IMMDevice dev = null;
        Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(0, 1, out dev));
        IAudioEndpointVolume epv = null;
        var epvid = typeof(IAudioEndpointVolume).GUID;
        Marshal.ThrowExceptionForHR(dev.Activate(ref epvid, 23, 0, out epv));
        return epv;
    }}
    public static float Volume {{
        get {{ float v = -1; Marshal.ThrowExceptionForHR(Vol().GetMasterVolumeLevelScalar(out v)); return v; }}
        set {{ Marshal.ThrowExceptionForHR(Vol().SetMasterVolumeLevelScalar(value, System.Guid.Empty)); }}
    }}
    public static bool Mute {{
        get {{ bool mute; Marshal.ThrowExceptionForHR(Vol().GetMute(out mute)); return mute; }}
        set {{ Marshal.ThrowExceptionForHR(Vol().SetMute(value, System.Guid.Empty)); }}
    }}
}}
'@
[Audio]::Volume = $volume
"""
    subprocess.run(
        ['powershell', '-command', script],
        capture_output=True, timeout=5
    )


def mute_volume():
    subprocess.run(
        ['powershell', '-command',
         '$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)'],
        capture_output=True
    )


def volume_up(amount: int = 10):
    try:
        current = _get_volume_ps()
        new_level = min(100, current + amount)
        _set_volume_ps(new_level)
        speak(f"Volume {new_level} percent, boss.")
        print(f"🔊 Volume: {new_level}%")
    except Exception as e:
        print(f"Volume error: {e}")
        speak("Couldn't change volume, boss.")


def volume_down(amount: int = 10):
    try:
        current = _get_volume_ps()
        new_level = max(0, current - amount)
        _set_volume_ps(new_level)
        speak(f"Volume {new_level} percent, boss.")
        print(f"🔉 Volume: {new_level}%")
    except Exception as e:
        print(f"Volume error: {e}")
        speak("Couldn't change volume, boss.")


def _get_volume_ps() -> int:
    """PowerShell se current volume lo."""
    result = subprocess.run(
        ['powershell', '-command', '''
        Add-Type -TypeDefinition @'
        using System.Runtime.InteropServices;
        [Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        interface IAudioEndpointVolume {
            int f(); int g(); int h(); int i();
            int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext);
            int j();
            int GetMasterVolumeLevelScalar(out float pfLevel);
            int k(); int l(); int m(); int n();
            int SetMute([MarshalAs(UnmanagedType.Bool)] bool bMute, System.Guid pguidEventContext);
            int GetMute(out bool pbMute);
        }
        [Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        interface IMMDevice {
            int Activate(ref System.Guid id, uint clsCtx, int activationParams, out IAudioEndpointVolume aev);
        }
        [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        interface IMMDeviceEnumerator {
            int f();
            int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
        }
        [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
        class MMDeviceEnumeratorComObject { }
        public class Audio {
            static IAudioEndpointVolume Vol() {
                var enumerator = new MMDeviceEnumeratorComObject() as IMMDeviceEnumerator;
                IMMDevice dev = null;
                Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(0, 1, out dev));
                IAudioEndpointVolume epv = null;
                var epvid = typeof(IAudioEndpointVolume).GUID;
                Marshal.ThrowExceptionForHR(dev.Activate(ref epvid, 23, 0, out epv));
                return epv;
            }
            public static float Volume {
                get { float v = -1; Marshal.ThrowExceptionForHR(Vol().GetMasterVolumeLevelScalar(out v)); return v; }
            }
        }
'@
        [Audio]::Volume * 100
        '''],
        capture_output=True, text=True, timeout=10
    )
    try:
        return int(float(result.stdout.strip().split('\n')[-1]))
    except:
        return 50


def _set_volume_ps(level: int):
    """PowerShell se volume set karo."""
    script = f'''
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {{
    int f(); int g(); int h(); int i();
    int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext);
    int j();
    int GetMasterVolumeLevelScalar(out float pfLevel);
    int k(); int l(); int m(); int n();
    int SetMute([MarshalAs(UnmanagedType.Bool)] bool bMute, System.Guid pguidEventContext);
    int GetMute(out bool pbMute);
}}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {{
    int Activate(ref System.Guid id, uint clsCtx, int activationParams, out IAudioEndpointVolume aev);
}}
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {{
    int f();
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
}}
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumeratorComObject {{ }}
public class Audio {{
    static IAudioEndpointVolume Vol() {{
        var enumerator = new MMDeviceEnumeratorComObject() as IMMDeviceEnumerator;
        IMMDevice dev = null;
        Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(0, 1, out dev));
        IAudioEndpointVolume epv = null;
        var epvid = typeof(IAudioEndpointVolume).GUID;
        Marshal.ThrowExceptionForHR(dev.Activate(ref epvid, 23, 0, out epv));
        return epv;
    }}
    public static float Volume {{
        set {{ Marshal.ThrowExceptionForHR(Vol().SetMasterVolumeLevelScalar(value, System.Guid.Empty)); }}
    }}
}}
'@
[Audio]::Volume = {level / 100}
'''
    subprocess.run(
        ['powershell', '-command', script],
        capture_output=True, timeout=10
    )


def mute():
    subprocess.run(
        ['powershell', '-command',
         '$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)'],
        capture_output=True
    )
    speak("Muted, boss.")
    print("🔇 Muted")


def unmute():
    subprocess.run(
        ['powershell', '-command',
         '$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)'],
        capture_output=True
    )
    speak("Unmuted, boss.")
    print("🔊 Unmuted")


def handle_volume_command(user_input: str) -> bool:
    u = user_input.lower()

    if any(t in u for t in ["unmute", "sound on", "awaaz on"]):
        unmute()
        return True

    if any(t in u for t in ["mute", "sound off", "awaaz band"]):
        mute()
        return True

    match = re.search(r'volume\s+(\d+)', u)
    if match:
        level = int(match.group(1))
        _set_volume_ps(level)
        speak(f"Volume set to {level} percent, boss.")
        return True

    if any(t in u for t in [
        "volume up", "volume badha", "awaaz badha",
        "louder", "tez karo", "volume increase"
    ]):
        match = re.search(r'(\d+)', u)
        amount = int(match.group(1)) if match else 10
        volume_up(amount)
        return True

    if any(t in u for t in [
        "volume down", "volume kam", "awaaz kam",
        "quieter", "soft karo", "volume decrease"
    ]):
        match = re.search(r'(\d+)', u)
        amount = int(match.group(1)) if match else 10
        volume_down(amount)
        return True

    if any(t in u for t in [
        "volume kya hai", "current volume",
        "volume kitna hai", "volume check"
    ]):
        current = _get_volume_ps()
        speak(f"Volume is at {current} percent, boss.")
        return True

    return False