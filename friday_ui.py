from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QBrush, QColor
from PyQt6.QtCore import Qt
import sys

class FridayUI(QWidget):
    def __init__(self):
        super().__init__()
        # 🔥 waveform data
        import random
        self.bars = [random.randint(10, 40) for _ in range(20)]
    #  animation variables
        self.radius = 70
        self.grow = True

        #  timer
        from PyQt6.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(60)

        self.setWindowTitle("FRIDAY")
        self.setGeometry(100, 100, 350, 500)

        # 🔥 remove title bar (modern look)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(QColor("#0b0b0b")))
        painter.drawRoundedRect(0, 0, 350, 500, 20, 20)

        # 🔥 glow circle
        color = QColor("#B7415D")
        painter.setBrush(QBrush(color))

        center_x = 175
        center_y = 250

        painter.drawEllipse(
            int(center_x - self.radius),
            int(center_y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2)
        )

        # 🔥 waveform bars
        bar_width = 6
        spacing = 4

        start_x = 50
        y_base = 420  # bottom line

        for i, height in enumerate(self.bars):
            x = start_x + i * (bar_width + spacing)

            painter.setBrush(QBrush(QColor("#B7415D")))
    
            painter.drawRoundedRect(
                int(x),
                int(y_base - height),
                bar_width,
                height,
                3, 3
            )

    def animate(self):
        if self.grow:
            self.radius += 0.5
            if self.radius > 90:
                self.grow = False
        else:
            self.radius -= 0.5
            if self.radius < 60:
                self.grow = True

        # 🔥 update waveform
        import random
        self.bars = [random.randint(10, 80) for _ in range(20)]
        
        self.update()
        

app = QApplication(sys.argv)        
window = FridayUI()
window.show()
sys.exit(app.exec())