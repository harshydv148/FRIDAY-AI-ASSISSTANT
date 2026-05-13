import os

USERNAME = os.getlogin()

WEB_APPS = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "github": "https://github.com",
    "problems": "https://leetcode.com",
    "gpt": "https://chat.openai.com",
    "instagram": "https://instagram.com",
    "linkedin": "https://linkedin.com",
    "twitter": "https://twitter.com",
    "gmail": "https://mail.google.com",
}

SYSTEM_APPS = {
    "notepad": "notepad",
    "vs code": "code",
    "code": "code",
    "telegram": "start shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop.Store",
    "calculator": "calc",
    "paint": "mspaint",
    "task manager": "taskmgr",
}

BROWSER_APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
}

APP_FIRST = {
    "instagram": {
        "app": "start shell:AppsFolder\\Facebook.InstagramBeta_8xx8rvfyw5nnt!App",
        "web": "https://instagram.com",
    },
    "whatsapp": {
        "app": "start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
        "web": "https://web.whatsapp.com",
    },
    "telegram": {
        "app": "start shell:AppsFolder\\TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm!Telegram.TelegramDesktop.Store",
        "web": "https://web.telegram.org",
    },
    "linkedin": {
        "app": "start shell:AppsFolder\\7EE7776C.LinkedInforWindows_w1wdnht996qgy!App",
        "web": "https://linkedin.com",
    },
    "snapchat": {
        "app": "start shell:AppsFolder\\CBSInteractive.Snapchat_kzf8qxf38zg5c!App",
        "web": "https://snapchat.com",
    },
    "spotify": {
        "app": "start shell:AppsFolder\\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
        "web": "https://open.spotify.com",
    },
    "twitter": {
        "app": "start shell:AppsFolder\\Twitter.Twitter_8xx8rvfyw5nnt!App",
        "web": "https://twitter.com",
    },
    "gpt": {
        "app": "start shell:AppsFolder\\OpenAI.ChatGPT-Desktop_2p2nqsd0c76g0!ChatGPT",
        "web": "https://chat.openai.com",
    },
}

common_apps = {
    "chrome", "firefox", "edge", "brave", "spotify",
    "discord", "telegram", "whatsapp", "instagram",
    "notepad", "calculator", "paint", "zoom", "vlc",
    "steam", "obs", "word", "excel",
}

PROTECTED_PROCESS_NAMES = {
    "code.exe", "code - insiders.exe",
    "cmd.exe", "powershell.exe", "powershell_ise.exe",
    "windowsterminal.exe", "wt.exe",
    "python.exe", "pythonw.exe", "python3.exe",
    "conhost.exe", "openconsole.exe",
    "explorer.exe", "taskmgr.exe",
    "node.exe", "electron.exe",
    "system", "smss.exe", "csrss.exe", "wininit.exe",
    "winlogon.exe", "services.exe", "lsass.exe",
    "svchost.exe", "dwm.exe", "fontdrvhost.exe",
    "registry", "tasklist.exe", "taskkill.exe",
    "sihost.exe", "ctfmon.exe", "spoolsv.exe",
    "runtimebroker.exe", "dllhost.exe", "audiodg.exe",
    "searchhost.exe", "searchindexer.exe",
    "shellexperiencehost.exe", "startmenuexperiencehost.exe",
    "textinputhost.exe", "applicationframehost.exe",
    "backgroundtaskhost.exe", "taskhostw.exe",
    "securityhealthservice.exe", "securityhealthsystray.exe",
    "msmpeng.exe", "nissrv.exe", "msiexec.exe",
    "smartscreen.exe", "lockapp.exe",
}