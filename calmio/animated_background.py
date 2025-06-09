import math

from PySide6.QtCore import (
    Qt,
    QTimer,
    Property,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QPointF,
)
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QPainterPath
from PySide6.QtWidgets import QWidget


class AnimatedBackground(QWidget):
    """Widget that displays an animated gradient cycling through chakra colors."""

    def _saturate(self, color: QColor, factor: float = 1.3) -> QColor:
        """Return a more saturated version of *color* keeping its value."""
        h, s, v, a = color.getHsv()
        s = min(255, int(s * factor))
        return QColor.fromHsv(h, s, v, a)

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)

        self.dark_mode = dark_mode
        self._color1 = QColor(255, 0, 0)
        self._color2 = QColor(255, 80, 80)

        self._opacity = 0.0

        self._ring_padding = 1.0

        self._angle = 0.0
        # Three halo rings rotating around the breathing circle
        # Increase spacing between rings and rotate all in the same direction
        self._rings = [
            {"radius": 0.30, "phase": 0.0, "speed": 0.002, "dir": 1},  # inner ring
            {"radius": 0.50, "phase": 1.0, "speed": 0.0015, "dir": 1},  # middle ring
            {"radius": 0.70, "phase": 2.0, "speed": 0.003, "dir": 1},  # outer ring
        ]
        self._offset_timer = QTimer(self)
        self._offset_timer.timeout.connect(self._update_offset)
        self._offset_timer.start(50)

        self._colors = self._chakra_colors()
        self._chakra_index = 0
        self.set_color1(self._colors[0])
        base2 = self._colors[0].lighter(150) if not self.dark_mode else self._colors[0].darker(150)
        self.set_color2(self._saturate(base2))
        self.color_anim = None
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

    def get_ring_padding(self):
        return self._ring_padding

    def set_ring_padding(self, value):
        self._ring_padding = max(0.1, float(value))
        self.update()

    ring_padding = Property(float, get_ring_padding, set_ring_padding)

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
            base = [c.darker(180) for c in base]
        return [self._saturate(c) for c in base]

    def set_dark_mode(self, value: bool) -> None:
        """Update dark mode setting and refresh colors."""
        if self.dark_mode == bool(value):
            return
        self.dark_mode = bool(value)
        self._colors = self._chakra_colors()
        current = self._colors[self._chakra_index]
        self.set_color1(current)
        base2 = current.lighter(150) if not self.dark_mode else current.darker(150)
        self.set_color2(self._saturate(base2))

    def chakra_colors(self):
        """Return the list of chakra colors."""
        return list(self._colors)

    def chakra_index(self):
        """Return the current chakra index."""
        return self._chakra_index

    def transition_to_index(self, index: int, duration: int = 2000):
        """Animate the gradient to the chakra color at the given index."""
        index %= len(self._colors)
        target = self._colors[index]
        if self.color_anim:
            self.color_anim.stop()
        group = QParallelAnimationGroup(self)

        a1 = QPropertyAnimation(self, b"color1")
        a1.setDuration(duration)
        a1.setStartValue(self._color1)
        a1.setEndValue(target)
        group.addAnimation(a1)

        target2 = target.lighter(150) if not self.dark_mode else target.darker(150)
        target2 = self._saturate(target2)
        a2 = QPropertyAnimation(self, b"color2")
        a2.setDuration(duration)
        a2.setStartValue(self._color2)
        a2.setEndValue(target2)
        group.addAnimation(a2)

        self.color_anim = group
        group.finished.connect(lambda: setattr(self, "_chakra_index", index))
        group.start()

    def _update_offset(self):
        self._angle += 0.001
        for ring in self._rings:
            ring["phase"] += ring["speed"] * ring["dir"]
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

        painter.setOpacity(self._opacity * 0.4)
        painter.setPen(Qt.NoPen)

        for ring in self._rings:
            path = QPainterPath()
            steps = 120
            base_radius = (
                min(rect.width(), rect.height())
                * ring["radius"]
                * self._ring_padding
            )
            amp = base_radius * 0.05
            freq = 6
            for i in range(steps + 1):
                angle = 2 * math.pi * i / steps + ring["phase"]
                r = base_radius + amp * math.sin(freq * angle)
                x = center.x() + r * math.cos(angle)
                y = center.y() + r * math.sin(angle)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            color = QColor(255, 255, 255, 80)
            painter.fillPath(path, color)

