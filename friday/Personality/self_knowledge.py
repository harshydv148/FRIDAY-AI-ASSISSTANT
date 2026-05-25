"""
Friday khud apna code padhti hai aur self-knowledge generate karti hai.
"""

import os


def get_module_summary() -> str:
    """
    friday/ folder ke actual files padho aur 
    summary banao ki kya kya defined hai.
    """
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    friday_dir = os.path.join(base, "friday")

    summary_lines = []

    scan_files = {
        "friday/Automation/apps.py": "App & process management",
        "friday/Automation/browser.py": "Browser & tab control",
        "friday/Automation/system.py": "System commands",
        "friday/Commands/screen.py": "Screen reading & OCR",
        "friday/Commands/files.py": "File handling & type command",
        "friday/Commands/shortcuts.py": "Shortcuts — time, date, greetings, standby",
        "friday/AI/intent.py": "Natural language intent detection",
        "friday/AI/chat.py": "Conversational AI",
        "friday/memory.py": "Memory system",
        "friday/voice.py": "Voice input/output",
        "friday/state.py": "Active/standby state management",
    }

    for rel_path, description in scan_files.items():
        full_path = os.path.join(base, rel_path.replace("/", os.sep))
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Functions dhundho
            functions = [
                line.strip().split("(")[0].replace("def ", "")
                for line in content.split("\n")
                if line.strip().startswith("def ")
            ]

            # Trigger lists dhundho
            triggers = [
                line.strip().split("=")[0].strip()
                for line in content.split("\n")
                if "TRIGGERS" in line or "triggers" in line.lower()
                and "=" in line
            ]

            summary_lines.append(
                f"- {rel_path} ({description}): "
                f"functions=[{', '.join(functions[:8])}]"
            )

    return "\n".join(summary_lines)


def get_recent_changes() -> str:
    """
    memory.json mein stored recent feature additions padho.
    """
    import json
    memory_path = "memory.json"
    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
        
        changes = memory.get("__friday_features__", [])
        if changes:
            return "Recent additions:\n" + "\n".join(f"- {c}" for c in changes)
    except:
        pass
    return ""


def log_new_feature(feature: str):
    """
    Jab Harsh koi naya feature add kare, usse memory mein save karo.
    """
    import json
    from datetime import datetime
    
    memory_path = "memory.json"
    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
    except:
        memory = {}

    features = memory.get("__friday_features__", [])
    entry = f"{feature} (added {datetime.now().strftime('%d %b %Y')})"
    
    if entry not in features:
        features.append(entry)
    
    memory["__friday_features__"] = features[-10:]  # last 10 rakho
    
    with open(memory_path, "w") as f:
        json.dump(memory, f, indent=4)
    
    print(f"✅ Feature logged: {feature}")