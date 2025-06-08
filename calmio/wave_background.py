import math
import time
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QWidget


class WaveBackground(QWidget):
    """Decorative animated waves for the light theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)

        self.layers = [
            {"amplitude": 20, "wavelength": 240, "speed": 0.002, "phase": 0.0, "color": QColor(77, 159, 255, 80)},
            {"amplitude": 25, "wavelength": 300, "speed": 0.0014, "phase": 1.0, "color": QColor(77, 159, 255, 60)},
            {"amplitude": 30, "wavelength": 360, "speed": 0.0010, "phase": 2.0, "color": QColor(77, 159, 255, 40)},
        ]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_phases)
        self.timer.start(50)

    def _update_phases(self):
        for layer in self.layers:
            layer["phase"] += layer["speed"]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        for layer in self.layers:
            path = QPainterPath()
            base_y = h * 0.65
            path.moveTo(0, h)
            for x in range(0, w + 1, 2):
                y = base_y + math.sin(x / layer["wavelength"] + layer["phase"]) * layer["amplitude"]
                path.lineTo(x, y)
            path.lineTo(w, h)
            path.closeSubpath()

            painter.setPen(Qt.NoPen)
            painter.setBrush(layer["color"])
            painter.drawPath(path)


