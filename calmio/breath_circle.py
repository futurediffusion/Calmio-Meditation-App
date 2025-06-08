from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
import time
from PySide6.QtGui import QPainter, QBrush, QColor, QRadialGradient, QPen
from PySide6.QtWidgets import QWidget


class BreathCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._radius = 60
        self.min_radius = 60
        self.max_radius = 140
        self.base_color = QColor(255, 140, 0)
        self.complement_color = QColor(0, 150, 136)
        self._color = self.base_color
        self.inhale_time = 4000
        self.exhale_time = 6000
        # Increase breathing times more gradually
        # Third inhale should be around 4.3 seconds (150ms per cycle)
        # Reduce progression speed by half
        self.increment = 75
        self.animation = None
        self.phase = 'idle'
        self.breath_count = 0
        self.cycle_valid = False
        self.count_changed_callback = None
        self.breath_started_callback = None
        self.breath_finished_callback = None
        self.exhale_started_callback = None
        self.breath_start_time = 0
        self.inhale_start_time = 0
        self.exhale_start_time = 0
        self._ripple_radius = 0
        self._ripple_opacity = 0.0
        self.ripple_anim = None
        self.setMinimumSize(self.max_radius * 2 + 20, self.max_radius * 2 + 20)

    def getRadius(self):
        return self._radius

    def setRadius(self, value):
        self._radius = value
        self.update()

    radius = Property(float, getRadius, setRadius)

    def getColor(self):
        return self._color

    def setColor(self, color):
        self._color = color
        self.update()

    color = Property(QColor, getColor, setColor)

    def getRippleRadius(self):
        return self._ripple_radius

    def setRippleRadius(self, value):
        self._ripple_radius = value
        self.update()

    ripple_radius = Property(float, getRippleRadius, setRippleRadius)

    def getRippleOpacity(self):
        return self._ripple_opacity

    def setRippleOpacity(self, value):
        self._ripple_opacity = value
        self.update()

    ripple_opacity = Property(float, getRippleOpacity, setRippleOpacity)

    def paintEvent(self, event):
        if self.width() <= 0 or self.height() <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center = self.rect().center()

        if self._ripple_opacity > 0:
            pen_color = QColor(self._color)
            pen_color.setAlphaF(min(1.0, max(0.0, self._ripple_opacity)))
            pen = QPen(pen_color)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center, self._ripple_radius, self._ripple_radius)

        
        gradient = QRadialGradient(center, self._radius)
        gradient.setColorAt(0, self._color.lighter(120))
        gradient.setColorAt(1, self._color.darker(150))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, self._radius, self._radius)

    def start_inhale(self):
        if self.phase != 'idle':
            return
        self.phase = 'inhaling'
        self.breath_start_time = time.perf_counter()
        self.inhale_start_time = self.breath_start_time
        if self.breath_started_callback:
            self.breath_started_callback()
        self.cycle_valid = False
        self.animate(self._radius, self.max_radius, self.inhale_time,
                     target_color=self.complement_color)

    def start_exhale(self):
        if self.phase != 'inhaling':
            return
        self.cycle_valid = self._radius >= self.max_radius - 1
        self.exhale_start_time = time.perf_counter()
        self.phase = 'exhaling'
        duration = self.exhale_time if self.cycle_valid else 2000
        if self.exhale_started_callback:
            self.exhale_started_callback(duration)
        self.animate(self._radius, self.min_radius, duration,
                     target_color=self.base_color)

    def animate(self, start, end, duration, target_color):
        if self.animation:
            self.animation.stop()
        self.animation = QParallelAnimationGroup(self)

        radius_anim = QPropertyAnimation(self, b"radius")
        radius_anim.setStartValue(start)
        radius_anim.setEndValue(end)
        radius_anim.setDuration(int(duration))
        radius_anim.setEasingCurve(QEasingCurve.InOutSine)

        color_anim = QPropertyAnimation(self, b"color")
        color_anim.setStartValue(self._color)
        color_anim.setEndValue(target_color)
        color_anim.setDuration(int(duration))
        color_anim.setEasingCurve(QEasingCurve.InOutSine)

        self.animation.addAnimation(radius_anim)
        self.animation.addAnimation(color_anim)
        self.animation.finished.connect(self.animation_finished)
        self.animation.start()

    def start_ripple(self):
        if self.ripple_anim:
            self.ripple_anim.stop()
        self.setRippleOpacity(0.6)
        seq = QSequentialAnimationGroup(self)
        durations = [1500, 1700, 1400]
        for dur in durations:
            group = QParallelAnimationGroup(self)
            r_anim = QPropertyAnimation(self, b"ripple_radius")
            r_anim.setStartValue(self._radius)
            r_anim.setEndValue(self._radius * 1.6)
            r_anim.setDuration(dur)
            r_anim.setEasingCurve(QEasingCurve.OutQuad)
            o_anim = QPropertyAnimation(self, b"ripple_opacity")
            o_anim.setStartValue(0.6)
            o_anim.setEndValue(0.0)
            o_anim.setDuration(dur)
            o_anim.setEasingCurve(QEasingCurve.OutQuad)
            group.addAnimation(r_anim)
            group.addAnimation(o_anim)
            seq.addAnimation(group)
            seq.addPause(300)
        seq.finished.connect(lambda: self.setRippleOpacity(0.0))
        self.ripple_anim = seq
        seq.start()

    def animation_finished(self):
        if self.phase == 'exhaling':
            if self.cycle_valid:
                exhale_end = time.perf_counter()
                duration = exhale_end - self.breath_start_time
                inhale_dur = self.exhale_start_time - self.inhale_start_time
                exhale_dur = exhale_end - self.exhale_start_time
                self.breath_count += 1
                if self.count_changed_callback:
                    self.count_changed_callback(self.breath_count)
                if self.breath_finished_callback:
                    self.breath_finished_callback(duration, inhale_dur, exhale_dur)
                self.inhale_time += self.increment
                self.exhale_time += self.increment
            self.breath_start_time = 0
            self.phase = 'idle'
        elif self.phase == 'inhaling':
            self.start_ripple()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_inhale()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_exhale()
            event.accept()
        else:
            super().mouseReleaseEvent(event)
