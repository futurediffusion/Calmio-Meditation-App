from PySide6.QtCore import (
    Qt,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    QObject,
)
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget


class _Wave(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self._radius = 0.0
        self._opacity = 0.0

    def getRadius(self):
        return self._radius

    def setRadius(self, value):
        self._radius = value
        self.parent().update()

    radius = Property(float, getRadius, setRadius)

    def getOpacity(self):
        return self._opacity

    def setOpacity(self, value):
        self._opacity = value
        self.parent().update()

    opacity = Property(float, getOpacity, setOpacity)


class WaveOverlay(QWidget):
    """Transparent widget that draws expanding waves from a center point."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._waves = []
        self._center = QPoint(0, 0)
        self._color = QColor(0, 0, 0)
        self.hide()

    def start_waves(self, center: QPoint, color: QColor):
        self._center = center
        self._color = QColor(color)
        diag = (self.width() ** 2 + self.height() ** 2) ** 0.5 * 1.5
        configs = [
            {"duration": 1500, "opacity": 0.25},
            {"duration": 3000, "opacity": 0.2},
            {"duration": 4500, "opacity": 0.15},
        ]
        for cfg in configs:
            wave = _Wave(self)
            wave.setRadius(0)
            wave.setOpacity(cfg["opacity"])
            self._waves.append(wave)
            anim = QPropertyAnimation(wave, b"radius", self)
            anim.setStartValue(0)
            anim.setEndValue(diag)
            anim.setDuration(cfg["duration"])
            anim.setEasingCurve(QEasingCurve.OutSine)
            anim.finished.connect(lambda w=wave: self._remove_wave(w))
            anim.start()
        self.show()

    def _remove_wave(self, wave):
        if wave in self._waves:
            self._waves.remove(wave)
        if not self._waves:
            self.hide()

    def paintEvent(self, event):
        if not self._waves:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for wave in list(self._waves):
            if wave._opacity <= 0:
                continue
            pen_color = QColor(self._color)
            pen_color.setAlphaF(min(1.0, max(0.0, wave._opacity)))
            pen = QPen(pen_color)
            pen.setWidth(4)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(self._center, int(wave._radius), int(wave._radius))


