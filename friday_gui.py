"""
FRIDAY GUI — PyQt6 based desktop interface.
Iron Man inspired dark theme.
"""

import sys
import threading
import time
import random
import math
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QScrollArea, QFrame,
    QPushButton, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QObject,
    QPropertyAnimation, QEasingCurve, QRect, QPoint
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen,
    QLinearGradient, QBrush, QRadialGradient,
    QConicalGradient
)

from friday.voice import speak, listen, is_speaking, _load_piper
from friday.state import FridayState
from friday.memory import get_memory, should_check_memory, extract_and_save
from friday.Commands.screen import handle_screen_command, continue_guide_session
from friday.Commands.files import handle_type_command
from friday.Commands.shortcuts import handle_shortcut
from friday.Automation.browser import handle_close_tabs
from friday.Automation.apps import handle_open_command, handle_close_apps
from friday.Automation.system import handle_system_command
from friday.AI.intent import detect_and_handle_intent
from friday.AI.chat import handle_chat, set_session_context
from friday.Commands.screenshot import handle_screenshot_command
from friday.Commands.timer import handle_timer_command
from friday.Commands.notes import handle_notes_command, restore_reminders, load_notes
from friday.Commands.weather import handle_weather_command
from friday.Commands.todo import handle_todo_command, load_todos
from friday.Commands.spotify import handle_spotify_command
from friday.Automation.volume import handle_volume_command
from friday.Commands.git_commands import handle_git_command
from friday.Commands.network import handle_network_command
from friday.Commands.camera import handle_camera_command
from friday.Commands.search import handle_search_command
from friday.Commands.clipboard import handle_clipboard_command, start_monitoring

# ─────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────
BG_DARK      = "#08090e"
BG_PANEL     = "#0d0f18"
BG_CARD      = "#111520"
ACCENT_BLUE  = "#00d4ff"
ACCENT_BLUE2 = "#0088cc"
ACCENT_RED   = "#ff3333"
ACCENT_GOLD  = "#ffd700"
TEXT_PRIMARY  = "#e8eaf0"
TEXT_DIM      = "#4a5568"
TEXT_SECONDARY= "#6b7280"
BORDER_COLOR  = "#1a2030"
SUCCESS_GREEN = "#00ff88"


# ─────────────────────────────────────────
# VOICE WORKER
# ─────────────────────────────────────────
class VoiceWorker(QObject):
    user_spoke      = pyqtSignal(str)
    friday_spoke    = pyqtSignal(str)
    status_changed  = pyqtSignal(str)
    listening_start = pyqtSignal()
    listening_stop  = pyqtSignal()
    speaking_start  = pyqtSignal()
    speaking_stop   = pyqtSignal()
    notes_updated   = pyqtSignal()
    todos_updated   = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.state   = FridayState()
        self.running = True
        # self._patch_speak()

    # def _patch_speak(self):
    #     """speak() function ko monkey patch karo taaki signal emit ho."""
    #     import friday.voice as voice_module
    #     original_speak = voice_module.speak
    #     worker_ref = self

        # def patched_speak(text: str):
        #     original_speak(text)
        #     worker_ref.friday_spoke.emit(text)

        # voice_module.speak = patched_speak

    def process_command(self, user_input: str):
        if continue_guide_session(user_input): return
        if handle_screen_command(user_input): return
        if should_check_memory(user_input):
            saved = extract_and_save(user_input)
            if saved:
                speak("Got it, noted.")
                return
        if handle_shortcut(user_input, self.state): return
        if handle_type_command(user_input): return
        if handle_screenshot_command(user_input): return
        if handle_clipboard_command(user_input): return
        if handle_camera_command(user_input): return
        if handle_timer_command(user_input): return
        if handle_notes_command(user_input):
            self.notes_updated.emit()
            return
        if handle_todo_command(user_input):
            self.todos_updated.emit()
            return
        if handle_weather_command(user_input): return
        if handle_open_command(user_input): return
        if handle_close_tabs(user_input): return
        if handle_close_apps(user_input): return
        if handle_volume_command(user_input): return
        if handle_spotify_command(user_input): return
        if handle_git_command(user_input): return
        if handle_network_command(user_input): return
        if handle_system_command(user_input): return
        if handle_search_command(user_input): return
        if detect_and_handle_intent(user_input, get_memory()): return
        handle_chat(user_input, get_memory())

    def run(self):
        _load_piper()
    
        # Speak patch karo — run method mein karo taaki sab imports ho chuke hon
        import friday.voice as _vm
        import friday.Commands.screen as _scr
        import friday.AI.chat as _chat
        import friday.Commands.weather as _weather
        import friday.Commands.search as _search
    
        _original_speak = _vm.speak
        _worker = self
    
        def _patched_speak(text: str):
            _original_speak(text)
            try:
                _worker.friday_spoke.emit(str(text))
            except:
                pass
    
        # Har module mein speak replace karo
        _vm.speak = _patched_speak
        _scr.speak = _patched_speak
        _chat.speak = _patched_speak
        _weather.speak = _patched_speak
        _search.speak = _patched_speak
    
        # Baaki imports
        import friday.Commands.notes as _notes
        import friday.Commands.todo as _todo
        import friday.Commands.timer as _timer
        import friday.Commands.screenshot as _ss
        import friday.Commands.files as _files
        import friday.Commands.shortcuts as _shortcuts
        import friday.Automation.apps as _apps
        import friday.Automation.browser as _browser
        import friday.Automation.system as _sys
        import friday.Automation.volume as _vol
        import friday.Commands.spotify as _spotify
        import friday.Commands.git_commands as _git
        import friday.Commands.network as _net
        import friday.Commands.camera as _cam
        import friday.Commands.clipboard as _clip
    
        for mod in [_notes, _todo, _timer, _ss, _files, _shortcuts,
                    _apps, _browser, _sys, _vol, _spotify, _git,
                    _net, _cam, _clip]:
            if hasattr(mod, 'speak'):
                mod.speak = _patched_speak
    
        restore_reminders()
        start_monitoring()
        self.status_changed.emit("STANDBY")
    
        
        restore_reminders()
        start_monitoring()
        self.status_changed.emit("STANDBY")

        while self.running:
            if self.state.is_timed_out() and not self.state.standby:
                self.state.go_standby()
                self.status_changed.emit("STANDBY")
                speak("Going on standby.")

            if self.state.standby:
                self.status_changed.emit("STANDBY")
                user_input = listen(silent=True)
            else:
                self.status_changed.emit("LISTENING")
                self.listening_start.emit()
                user_input = listen()
                self.listening_stop.emit()

            if not user_input:
                continue

            self.user_spoke.emit(user_input)

            if self.state.standby:
                if any(p in user_input.lower() for p in [
                    "friday", "wake up friday", "utho friday"
                ]):
                    self.state.wake()
                    reply = "Back online, boss."
                    self.speaking_start.emit()
                    speak(reply)
                    self.speaking_stop.emit()
                    self.friday_spoke.emit(reply)
                    self.status_changed.emit("ACTIVE")
                continue

            if "friday" in user_input.lower():
                self.state.wake()
                user_input = user_input.lower().replace("friday", "").strip()
                if not user_input:
                    reply = random.choice([
                        "Yeah boss?", "Hey! What's up?",
                        "Listening, boss.", "What's good?",
                    ])
                    self.speaking_start.emit()
                    speak(reply)
                    self.speaking_stop.emit()
                    self.friday_spoke.emit(reply)
                    self.state.touch()
                    continue

            if not self.state.active:
                continue

            if user_input.lower().strip() == "exit":
                reply = "Later, boss."
                speak(reply)
                self.friday_spoke.emit(reply)
                self.running = False
                QApplication.quit()
                return

            self.status_changed.emit("THINKING")
            self.speaking_start.emit()
            self.process_command(user_input)
            self.speaking_stop.emit()
            self.state.touch()
            self.status_changed.emit("LISTENING")


# ─────────────────────────────────────────
# FRIDAY LOGO ANIMATION
# ─────────────────────────────────────────
class FridayLogoWidget(QWidget):
    """
    Animated FRIDAY logo — rotating rings + pulse.
    Active hone pe animate karta hai.
    """

    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self._angle      = 0.0
        self._pulse      = 0.0
        self._pulse_dir  = 1
        self._active     = False
        self._speaking   = False

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(30)

    def set_active(self, active: bool, speaking: bool = False):
        self._active   = active
        self._speaking = speaking

    def _tick(self):
        if self._active:
            self._angle += 3.0
            self._pulse += 0.06 * self._pulse_dir
            if self._pulse >= 1.0:
                self._pulse_dir = -1
            elif self._pulse <= 0.0:
                self._pulse_dir = 1
        else:
            self._angle += 0.4
            self._pulse += 0.02 * self._pulse_dir
            if self._pulse >= 1.0:
                self._pulse_dir = -1
            elif self._pulse <= 0.0:
                self._pulse_dir = 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width()  // 2
        cy = self.height() // 2

        color = ACCENT_RED if self._speaking else ACCENT_BLUE

        # Outer rotating ring
        p.setPen(QPen(QColor(color), 1.5, Qt.PenStyle.DashLine))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.save()
        p.translate(cx, cy)
        p.rotate(self._angle)
        p.drawEllipse(-70, -70, 140, 140)
        p.restore()

        # Middle ring
        p.setPen(QPen(QColor(color), 1, Qt.PenStyle.DotLine))
        p.save()
        p.translate(cx, cy)
        p.rotate(-self._angle * 1.5)
        p.drawEllipse(-52, -52, 104, 104)
        p.restore()

        # Pulse circle
        pulse_r = int(30 + self._pulse * 10)
        c = QColor(color)
        c.setAlpha(int(60 + self._pulse * 80))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(c))
        p.drawEllipse(cx - pulse_r, cy - pulse_r, pulse_r*2, pulse_r*2)

        # Core circle
        p.setBrush(QBrush(QColor(BG_DARK)))
        p.setPen(QPen(QColor(color), 2))
        p.drawEllipse(cx-28, cy-28, 56, 56)

        # FRIDAY text inside
        p.setPen(QColor(color))
        f = QFont("Consolas", 7, QFont.Weight.Bold)
        p.setFont(f)
        p.drawText(QRect(cx-28, cy-8, 56, 16),
                   Qt.AlignmentFlag.AlignCenter, "FRIDAY")

        # Dots on outer ring
        for i in range(8):
            angle_rad = math.radians(self._angle + i * 45)
            dx = int(70 * math.cos(angle_rad))
            dy = int(70 * math.sin(angle_rad))
            dot_c = QColor(color)
            dot_c.setAlpha(180 if i % 2 == 0 else 80)
            p.setBrush(QBrush(dot_c))
            p.setPen(Qt.PenStyle.NoPen)
            r = 4 if i % 2 == 0 else 2
            p.drawEllipse(cx + dx - r, cy + dy - r, r*2, r*2)


# ─────────────────────────────────────────
# VOICE VISUALIZER
# ─────────────────────────────────────────
class VoiceVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(50)
        self.bars     = [0.05] * 24
        self._active  = False
        self._speaking = False

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(60)

    def set_active(self, active: bool, speaking: bool = False):
        self._active   = active
        self._speaking = speaking

    def _tick(self):
        if self._active:
            for i in range(len(self.bars)):
                t = random.uniform(0.2, 1.0)
                self.bars[i] = self.bars[i]*0.5 + t*0.5
        else:
            for i in range(len(self.bars)):
                self.bars[i] = self.bars[i]*0.85 + 0.03*0.15
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w  = self.width()
        h  = self.height()
        bw = w / len(self.bars)
        g  = 2
        color = ACCENT_RED if self._speaking else ACCENT_BLUE

        for i, bh_ratio in enumerate(self.bars):
            x  = int(i * bw + g)
            bw_ = int(bw - g*2)
            bh  = int(bh_ratio * h * 0.85)
            y   = (h - bh) // 2

            grad = QLinearGradient(x, y, x, y+bh)
            c1 = QColor(color); c1.setAlpha(220)
            c2 = QColor(color); c2.setAlpha(60)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(x, y, bw_, bh, 4, 4)


# ─────────────────────────────────────────
# CHAT BUBBLE
# ─────────────────────────────────────────
class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        ts    = datetime.now().strftime("%H:%M")
        name  = "YOU" if is_user else "FRIDAY"
        nc    = ACCENT_GOLD if is_user else ACCENT_BLUE

        top = QHBoxLayout()
        top = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            f"color:{nc};font-size:10px;font-weight:bold;"
            f"font-family:'Consolas',monospace;letter-spacing:2px;"
        )
        ts_lbl = QLabel(ts)
        ts_lbl.setStyleSheet(
            f"color:{TEXT_DIM};font-size:10px;"
            f"font-family:'Consolas',monospace;"
        )
        top.addWidget(name_lbl)
        top.addStretch()
        top.addWidget(ts_lbl)
        layout.addLayout(top)

        # "(" character remove karo agar hai
        clean_text = text.lstrip("(").strip()
        msg = QLabel(clean_text)
        msg.setWordWrap(True)
        msg.setStyleSheet(
            f"color:{TEXT_PRIMARY};font-size:13px;"
            f"font-family:'Segoe UI',sans-serif;line-height:1.6;"
        )
        layout.addWidget(msg)

        bg  = "#141a28" if is_user else "#0c1218"
        bdr = ACCENT_GOLD if is_user else ACCENT_BLUE
        self.setStyleSheet(f"""
            QFrame {{
                background:{bg};
                border-left:2px solid {bdr};
                border-radius:8px;
                margin:3px 0px;
            }}
        """)


# ─────────────────────────────────────────
# SIDE CARD
# ─────────────────────────────────────────
class SideCard(QFrame):
    def __init__(self, title: str, color: str = ACCENT_BLUE):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 10, 12, 10)
        self._layout.setSpacing(6)

        t = QLabel(title)
        t.setStyleSheet(
            f"color:{color};font-size:10px;font-weight:bold;"
            f"font-family:'Consolas',monospace;letter-spacing:1px;"
        )
        self._layout.addWidget(t)

        self._content = QLabel("—")
        self._content.setWordWrap(True)
        self._content.setStyleSheet(
            f"color:{TEXT_SECONDARY};font-size:12px;"
            f"font-family:'Segoe UI',sans-serif;"
        )
        self._layout.addWidget(self._content)

        self.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD};
                border:1px solid {BORDER_COLOR};
                border-top:2px solid {color};
                border-radius:8px;
            }}
        """)

    def update_content(self, text: str):
        self._content.setText(text)


# ─────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F.R.I.D.A.Y.")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 780)
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background:{BG_DARK}; color:{TEXT_PRIMARY}; }}
            QScrollArea {{ border:none; background:transparent; }}
            QScrollBar:vertical {{
                background:{BG_PANEL}; width:5px; border-radius:2px;
            }}
            QScrollBar::handle:vertical {{
                background:{ACCENT_BLUE}; border-radius:2px; min-height:20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height:0px;
            }}
        """)
        self._build_ui()
        self._start_voice_thread()

        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._refresh_side)
        self._refresh_timer.start(3000)

        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0,0,0,0)
        root_layout.setSpacing(0)

        # ── Header ──────────────────────────────
        hdr = QFrame()
        hdr.setFixedHeight(54)
        hdr.setStyleSheet(
            f"background:{BG_PANEL};"
            f"border-bottom:1px solid {BORDER_COLOR};"
        )
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(24,0,24,0)

        logo_text = QLabel("F·R·I·D·A·Y")
        logo_text.setStyleSheet(
            f"color:{ACCENT_BLUE};font-size:20px;font-weight:bold;"
            f"font-family:'Consolas',monospace;letter-spacing:4px;"
        )
        hl.addWidget(logo_text)

        sub = QLabel("Fully Responsive Intelligent Digital Assistant for You")
        sub.setStyleSheet(
            f"color:{TEXT_DIM};font-size:11px;"
            f"font-family:'Segoe UI',sans-serif;"
        )
        hl.addWidget(sub)
        hl.addStretch()

        self._status_lbl = QLabel("● INITIALIZING")
        self._status_lbl.setStyleSheet(
            f"color:{ACCENT_GOLD};font-size:12px;"
            f"font-family:'Consolas',monospace;font-weight:bold;"
        )
        hl.addWidget(self._status_lbl)
        root_layout.addWidget(hdr)

        # ── Body ────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0,0,0,0)
        body.setSpacing(0)

        # ── LEFT — Logo + Chat ──────────────────
        left = QWidget()
        ll   = QVBoxLayout(left)
        ll.setContentsMargins(20,16,10,16)
        ll.setSpacing(12)

        # Logo + chat stacked
        center_area = QWidget()
        center_layout = QVBoxLayout(center_area)
        center_layout.setContentsMargins(0,0,0,0)
        center_layout.setSpacing(8)

        # Logo row — centered
        logo_row = QHBoxLayout()
        logo_row.addStretch()
        self._logo = FridayLogoWidget()
        logo_row.addWidget(self._logo)
        logo_row.addStretch()
        center_layout.addLayout(logo_row)

        # Conversation label
        conv_lbl = QLabel("CONVERSATION")
        conv_lbl.setStyleSheet(
            f"color:{TEXT_DIM};font-size:10px;"
            f"font-family:'Consolas',monospace;letter-spacing:2px;"
        )
        center_layout.addWidget(conv_lbl)

        # Chat scroll
        self._chat_scroll = QScrollArea()
        self._chat_scroll.setWidgetResizable(True)
        self._chat_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._chat_container = QWidget()
        self._chat_layout    = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(0,0,0,0)
        self._chat_layout.setSpacing(4)
        self._chat_layout.addStretch()
        self._chat_scroll.setWidget(self._chat_container)
        center_layout.addWidget(self._chat_scroll, stretch=1)

        ll.addWidget(center_area, stretch=1)

        # Visualizer
        self._viz = VoiceVisualizer()
        ll.addWidget(self._viz)

        body.addWidget(left, stretch=3)

        # Divider
        div = QFrame()
        div.setFixedWidth(1)
        div.setStyleSheet(f"background:{BORDER_COLOR};")
        body.addWidget(div)

        # ── RIGHT — Side Panel ──────────────────
        right = QWidget()
        right.setFixedWidth(270)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(10,16,20,16)
        rl.setSpacing(12)

        panel_lbl = QLabel("SYSTEM PANEL")
        panel_lbl.setStyleSheet(
            f"color:{TEXT_DIM};font-size:10px;"
            f"font-family:'Consolas',monospace;letter-spacing:2px;"
        )
        rl.addWidget(panel_lbl)

        self._notes_card = SideCard("ACTIVE NOTES", SUCCESS_GREEN)
        rl.addWidget(self._notes_card)

        self._todo_card = SideCard("TODO LIST", ACCENT_GOLD)
        rl.addWidget(self._todo_card)

        self._time_card = SideCard("SYSTEM TIME", ACCENT_BLUE)
        rl.addWidget(self._time_card)

        # Status card
        self._sys_card = SideCard("QUICK STATUS", ACCENT_RED)
        rl.addWidget(self._sys_card)
        self._sys_card.update_content(
            "Voice: Piper Amy\n"
            "LLM: Groq llama-3.3-70b\n"
            "Search: DuckDuckGo\n"
            "Music: yt-dlp"
        )

        rl.addStretch()
        body.addWidget(right)
        root_layout.addLayout(body, stretch=1)

    def _start_voice_thread(self):
        self._vthread = QThread()
        self._worker  = VoiceWorker()
        self._worker.moveToThread(self._vthread)

        self._vthread.started.connect(self._worker.run)
        self._worker.user_spoke.connect(
            lambda t: self._add_bubble(t, True)
        )
        self._worker.friday_spoke.connect(
            lambda t: self._add_bubble(t, False)
        )
        self._worker.status_changed.connect(self._on_status)
        self._worker.listening_start.connect(
            lambda: self._viz.set_active(True, False)
        )
        self._worker.listening_stop.connect(
            lambda: self._viz.set_active(False)
        )
        self._worker.speaking_start.connect(
            lambda: (
                self._viz.set_active(True, True),
                self._logo.set_active(True, True)
            )
        )
        self._worker.speaking_stop.connect(
            lambda: (
                self._viz.set_active(False),
                self._logo.set_active(False)
            )
        )
        self._worker.notes_updated.connect(self._refresh_side)
        self._worker.todos_updated.connect(self._refresh_side)

        self._vthread.start()

    def _add_bubble(self, text: str, is_user: bool):
        bubble = ChatBubble(text, is_user)
        self._chat_layout.insertWidget(
            self._chat_layout.count() - 1, bubble
        )
        QTimer.singleShot(
            80,
            lambda: self._chat_scroll.verticalScrollBar().setValue(
                self._chat_scroll.verticalScrollBar().maximum()
            )
        )

    def _on_status(self, status: str):
        colors = {
            "LISTENING": ACCENT_BLUE,
            "THINKING":  ACCENT_GOLD,
            "STANDBY":   TEXT_DIM,
            "ACTIVE":    SUCCESS_GREEN,
        }
        c = colors.get(status, TEXT_PRIMARY)
        self._status_lbl.setText(f"● {status}")
        self._status_lbl.setStyleSheet(
            f"color:{c};font-size:12px;"
            f"font-family:'Consolas',monospace;font-weight:bold;"
        )
        active = status in ("LISTENING", "THINKING", "ACTIVE")
        self._logo.set_active(active, status == "THINKING")

    def _update_clock(self):
        now = datetime.now().strftime("%A, %d %b %Y\n%H:%M:%S")
        self._time_card.update_content(now)

    def _refresh_side(self):
        # Notes
        try:
            notes = load_notes()
            pending = [n for n in notes if not n.get("reminded")]
            if pending:
                txt = "\n".join(
                    f"• {n['content'][:38]}{'...' if len(n['content'])>38 else ''}"
                    for n in pending[:4]
                )
            else:
                txt = "No active notes"
            self._notes_card.update_content(txt)
        except: pass

        # Todos
        try:
            todos = load_todos()
            pending = [t for t in todos if not t.get("done")]
            if pending:
                txt = "\n".join(
                    f"□ {t['task'][:36]}{'...' if len(t['task'])>36 else ''}"
                    for t in pending[:4]
                )
            else:
                txt = "All clear! ✓"
            self._todo_card.update_content(txt)
        except: pass

    def closeEvent(self, event):
        self._worker.running = False
        self._vthread.quit()
        self._vthread.wait()
        event.accept()


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FRIDAY")
    app.setFont(QFont("Segoe UI", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()