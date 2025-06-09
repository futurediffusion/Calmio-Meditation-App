from PySide6.QtCore import (
    Qt,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QSequentialAnimationGroup,
    QTimer,
    QObject,
)
import time
import random
from PySide6.QtGui import QPainter, QBrush, QColor, QRadialGradient, QPen
from PySide6.QtWidgets import QWidget


class Ripple(QObject):
    """Helper object representing a single expanding ring."""

    def __init__(self, parent, radius):
        super().__init__(parent)
        self._radius = radius
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
        self.speed_multiplier = 1.0
        self.animation = None
        self.phase = 'idle'
        self.breath_count = 0
        self.cycle_valid = False
        self.count_changed_callback = None
        self.breath_started_callback = None
        self.breath_finished_callback = None
        self.exhale_started_callback = None
        self.inhale_finished_callback = None
        self.ripple_spawned_callback = None
        self.breath_start_time = 0
        self.inhale_start_time = 0
        self.exhale_start_time = 0
        self._ripple_radius = 0
        self._ripple_opacity = 0.0
        self.ripple_anim = None
        self.ripples = []
        self.pattern = None
        self.phase_index = 0
        self.phase_colors = []
        self.pattern_anim = None
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

        ripples = list(self.ripples)
        if self._ripple_opacity > 0:
            temp = Ripple(self, self._ripple_radius)
            temp._opacity = self._ripple_opacity
            ripples.append(temp)

        for ripple in ripples:
            if ripple._opacity <= 0:
                continue
            pen_color = QColor(self._color)
            pen_color.setAlphaF(min(1.0, max(0.0, ripple._opacity)))
            pen = QPen(pen_color)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center, ripple._radius, ripple._radius)

        
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
        dur = self.inhale_time / self.speed_multiplier
        self.animate(
            self._radius,
            self.max_radius,
            dur,
            target_color=self.complement_color,
        )

    def start_exhale(self):
        if self.phase != 'inhaling':
            return
        self.cycle_valid = self._radius >= self.max_radius - 1
        self.exhale_start_time = time.perf_counter()
        self.phase = 'exhaling'
        duration = self.exhale_time if self.cycle_valid else 2000
        duration /= self.speed_multiplier
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
        radius_anim.setDuration(int(duration / self.speed_multiplier))
        radius_anim.setEasingCurve(QEasingCurve.InOutSine)

        color_anim = QPropertyAnimation(self, b"color")
        color_anim.setStartValue(self._color)
        color_anim.setEndValue(target_color)
        color_anim.setDuration(int(duration / self.speed_multiplier))
        color_anim.setEasingCurve(QEasingCurve.InOutSine)

        self.animation.addAnimation(radius_anim)
        self.animation.addAnimation(color_anim)
        self.animation.finished.connect(self.animation_finished)
        self.animation.start()

    def start_ripple(self):
        if self.ripple_anim:
            self.ripple_anim.stop()

        # base ripple using legacy properties
        self.setRippleOpacity(0.4)
        base_group = QParallelAnimationGroup(self)
        r_anim = QPropertyAnimation(self, b"ripple_radius")
        r_anim.setStartValue(self._radius)
        r_anim.setEndValue(self._radius * 1.5)
        r_anim.setDuration(int(2000 / self.speed_multiplier))
        r_anim.setEasingCurve(QEasingCurve.InOutSine)
        o_anim = QPropertyAnimation(self, b"ripple_opacity")
        o_anim.setStartValue(0.4)
        o_anim.setEndValue(0.0)
        o_anim.setDuration(int(2000 / self.speed_multiplier))
        o_anim.setEasingCurve(QEasingCurve.InOutSine)
        base_group.addAnimation(r_anim)
        base_group.addAnimation(o_anim)
        base_group.finished.connect(lambda: self.setRippleOpacity(0.0))

        # Play only the base ripple animation
        self.ripple_anim = base_group
        base_group.start()
        if self.ripple_spawned_callback:
            center = self.mapTo(self.window(), self.rect().center())
            self.ripple_spawned_callback(center, self._color)

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
            if self.inhale_finished_callback:
                self.inhale_finished_callback()

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

    # ------------------------------------------------------------------
    def _generate_phase_colors(self, n: int):
        colors = [self.base_color, self.complement_color]
        if n <= 2:
            return colors[:n]
        extra = []
        for i in range(n - 2):
            if i % 2 == 0:
                extra.append(self.base_color.lighter(120 + i * 10))
            else:
                extra.append(self.complement_color.darker(120 + i * 10))
        return colors + extra

    def set_pattern(self, pattern: list[dict]):
        self.pattern = pattern
        self.phase_colors = self._generate_phase_colors(len(pattern))
        if self.pattern_anim:
            self.pattern_anim.stop()
            self.pattern_anim = None

    def start_pattern(self):
        if not self.pattern:
            return
        if self.pattern_anim and self.pattern_anim.state() != QPropertyAnimation.Stopped:
            self.pattern_anim.stop()
        self.pattern_anim = self._build_pattern_animation()
        self.pattern_anim.start()

    def stop_pattern(self):
        if self.pattern_anim:
            self.pattern_anim.stop()
            self.pattern_anim = None

    def _build_pattern_animation(self):
        group = QSequentialAnimationGroup(self)
        radius = self.min_radius
        color = self.base_color
        for idx, phase in enumerate(self.pattern):
            dur = int(phase.get("duration", 1) * 1000 / self.speed_multiplier)
            target_color = self.phase_colors[idx]
            name = phase.get("name", "").lower()
            start_radius = radius
            end_radius = radius
            if "inh" in name:
                end_radius = self.max_radius
            elif "exh" in name:
                end_radius = self.min_radius
            r_anim = QPropertyAnimation(self, b"radius")
            r_anim.setDuration(dur)
            r_anim.setStartValue(start_radius)
            r_anim.setEndValue(end_radius)
            r_anim.setEasingCurve(QEasingCurve.InOutSine)
            c_anim = QPropertyAnimation(self, b"color")
            c_anim.setDuration(dur)
            c_anim.setStartValue(color)
            c_anim.setEndValue(target_color)
            c_anim.setEasingCurve(QEasingCurve.InOutSine)
            pg = QParallelAnimationGroup()
            pg.addAnimation(r_anim)
            pg.addAnimation(c_anim)
            if idx < len(self.pattern) - 1:
                pg.finished.connect(self.start_ripple)
            group.addAnimation(pg)
            radius = end_radius
            color = target_color
        group.finished.connect(self.start_pattern)
        return group
