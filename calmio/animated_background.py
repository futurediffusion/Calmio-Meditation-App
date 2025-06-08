import math

from PySide6.QtCore import (
    Qt,
    QTimer,
    Property,
    QSequentialAnimationGroup,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QPointF,
)
from PySide6.QtGui import QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget


class AnimatedBackground(QWidget):
    """Widget that displays an animated gradient cycling through chakra colors."""

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)

        self.dark_mode = dark_mode
        self._color1 = QColor(255, 0, 0)
        self._color2 = QColor(255, 80, 80)

        self._opacity = 0.0

        self._angle = 0.0
        self._offset_timer = QTimer(self)
        self._offset_timer.timeout.connect(self._update_offset)
        self._offset_timer.start(50)

        self._build_animation()
        self.show()

    # Property definitions
    def get_color1(self):
        return self._color1

    def set_color1(self, color):
        self._color1 = color
        self.update()

    color1 = Property(QColor, get_color1, set_color1)

    def get_color2(self):
        return self._color2

    def set_color2(self, color):
        self._color2 = color
        self.update()

    color2 = Property(QColor, get_color2, set_color2)

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = max(0.0, min(1.0, float(value)))
        self.update()

    opacity = Property(float, get_opacity, set_opacity)

    def _chakra_colors(self):
        base = [
            QColor(220, 20, 60),    # red
            QColor(255, 140, 0),    # orange
            QColor(255, 215, 0),    # yellow
            QColor(76, 175, 80),    # green
            QColor(33, 150, 243),   # blue
            QColor(75, 0, 130),     # indigo
            QColor(138, 43, 226),   # violet
        ]
        if self.dark_mode:
            return [c.darker(180) for c in base]
        return base

    def _build_animation(self):
        colors = self._chakra_colors()
        duration = 255000  # 4 min 15 sec per color

        self.anim = QSequentialAnimationGroup(self)
        for i in range(len(colors)):
            start = colors[i]
            end = colors[(i + 1) % len(colors)]

            group = QParallelAnimationGroup(self)

            a1 = QPropertyAnimation(self, b"color1")
            a1.setDuration(duration)
            a1.setStartValue(start)
            a1.setEndValue(end)
            group.addAnimation(a1)

            start2 = start.lighter(150) if not self.dark_mode else start.darker(150)
            end2 = end.lighter(150) if not self.dark_mode else end.darker(150)

            a2 = QPropertyAnimation(self, b"color2")
            a2.setDuration(duration)
            a2.setStartValue(start2)
            a2.setEndValue(end2)
            group.addAnimation(a2)

            self.anim.addAnimation(group)

        self.anim.setLoopCount(-1)
        self.anim.start()

    def _update_offset(self):
        self._angle += 0.002
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        painter.fillRect(rect, QColor("white"))
        if self._opacity <= 0:
            return
        painter.setRenderHint(QPainter.Antialiasing)
        radius = max(rect.width(), rect.height()) * 0.75
        center = rect.center()
        offset_center = QPointF(
            center.x() + radius * 0.2 * math.cos(self._angle),
            center.y() + radius * 0.2 * math.sin(self._angle),
        )
        gradient = QRadialGradient(offset_center, radius)
        gradient.setColorAt(0, self._color1)
        gradient.setColorAt(1, self._color2)
        painter.setOpacity(self._opacity)
        painter.fillRect(rect, gradient)

