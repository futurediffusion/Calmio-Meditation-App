from PySide6.QtCore import (
    Qt,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    QObject,
    QParallelAnimationGroup,
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
        # Create a single, slower wave instead of multiple ones
        wave = _Wave(self)
        wave.setRadius(0)
        wave.setOpacity(0.2)
        self._waves.append(wave)

        group = QParallelAnimationGroup(self)

        r_anim = QPropertyAnimation(wave, b"radius", self)
        r_anim.setStartValue(0)
        r_anim.setEndValue(diag)
        r_anim.setDuration(12000)
        r_anim.setEasingCurve(QEasingCurve.OutCubic)
        group.addAnimation(r_anim)

        o_anim = QPropertyAnimation(wave, b"opacity", self)
        o_anim.setStartValue(0.2)
        o_anim.setEndValue(0.0)
        o_anim.setDuration(12000)
        o_anim.setEasingCurve(QEasingCurve.InQuad)
        group.addAnimation(o_anim)

        group.finished.connect(lambda w=wave: self._remove_wave(w))
        group.start()
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
        if not painter.isActive():
            return
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
        painter.end()

