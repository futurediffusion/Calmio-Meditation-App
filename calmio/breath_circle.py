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
        # Third color completing a balanced triad
        self.retention_color = QColor(139, 0, 255)
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
        self.pattern_states = []
        self.key_pressed = False
        self.released_during_exhale = False
        self.hold_timer = QTimer(self)
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self._on_hold_finished)
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

    def start_inhale(self, color=None, duration=None):
        if self.phase not in ('idle', 'holding'):
            return
        self.phase = 'inhaling'
        self.breath_start_time = time.perf_counter()
        self.inhale_start_time = self.breath_start_time
        if self.breath_started_callback:
            self.breath_started_callback()
        self.cycle_valid = False
        dur = (duration or self.inhale_time) / self.speed_multiplier
        self.animate(
            self._radius,
            self.max_radius,
            dur,
            target_color=color or self.complement_color,
        )

    def start_exhale(self, color=None, duration=None):
        if self.phase not in ("inhaling", "holding"):
            return
        # Treat early release during the hold phase as an incomplete cycle
        self.cycle_valid = (
            self._radius >= self.max_radius - 1
            and (self.phase != "holding" or not self.hold_timer.isActive())
        )
        self.exhale_start_time = time.perf_counter()
        if self.phase == "holding" and self.hold_timer.isActive():
            # Trigger ripple/wave when exiting a hold early
            self.start_ripple()
        self.phase = 'exhaling'
        dur = (duration if duration is not None else (self.exhale_time if self.cycle_valid else 2000))
        dur /= self.speed_multiplier
        if self.exhale_started_callback:
            self.exhale_started_callback(dur)
        self.animate(self._radius, self.min_radius, dur,
                     target_color=color or self.base_color)

    def start_hold(self, color=None, duration=None):
        """Animate color transition during the retention phase."""
        if self.animation:
            self.animation.stop()
        self.phase = 'holding'
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setStartValue(self._color)
        self.animation.setEndValue(color or self.retention_color)
        dur = int((duration or 0) / self.speed_multiplier)
        self.animation.setDuration(dur)
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        self.animation.start()
        self.hold_timer.start(dur)

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
                # Reset flag before callbacks so listeners see final state
                self.released_during_exhale = False
                if self.count_changed_callback:
                    self.count_changed_callback(self.breath_count)
                if self.breath_finished_callback:
                    self.breath_finished_callback(duration, inhale_dur, exhale_dur)
                self.inhale_time += self.increment
                self.exhale_time += self.increment
            self.breath_start_time = 0
            self.phase = 'idle'
            self.released_during_exhale = False
        elif self.phase == 'inhaling':
            self.start_ripple()
            if self.inhale_finished_callback:
                self.inhale_finished_callback()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_press()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_release()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def set_pattern(self, pattern: list[dict]):
        self.pattern = pattern
        self.phase_index = 0
        self.phase_colors = []
        self.pattern_states = []
        total = len(pattern)
        for i, ph in enumerate(pattern):
            name = ph.get("name", "").lower()
            if "inh" in name:
                self.phase_colors.append(self.complement_color)
                expected = True
            elif "exh" in name:
                self.phase_colors.append(self.base_color)
                expected = False
            else:
                # Hold phase keeps the current key state
                self.phase_colors.append(self.retention_color)
                if i == 0:
                    expected = True
                else:
                    expected = self.pattern_states[i - 1]
            self.pattern_states.append(expected)
        self.stop_animation()

    def stop_animation(self):
        if self.animation:
            self.animation.stop()
            self.animation = None
        if self.hold_timer.isActive():
            self.hold_timer.stop()

    def _on_hold_finished(self):
        self.start_ripple()
        if self.inhale_finished_callback:
            self.inhale_finished_callback()
        self.phase_index += 1
        if self.phase_index >= len(self.pattern):
            self.phase_index = 0
        self.phase = 'holding'
        expected = self.pattern_states[self.phase_index]
        if expected == self.key_pressed:
            self._start_phase(self.phase_index)

    def on_press(self):
        self.key_pressed = True
        if not self.pattern:
            self.start_inhale()
        else:
            if self.hold_timer.isActive():
                self.hold_timer.stop()
            self._maybe_start_phase()

    def on_release(self):
        self.key_pressed = False
        if self.phase == "exhaling" and self.animation:
            self.released_during_exhale = True
            if not self.pattern:
                # Keep current exhale animation so it matches pattern behavior
                return
        if not self.pattern:
            self.start_exhale()
        else:
            hold_active = self.hold_timer.isActive()
            if self.phase in ("inhaling", "holding"):
                # Interrupt cycle and reset
                # Call start_exhale before stopping the hold timer so the
                # cycle is marked invalid when releasing early from a hold
                self.released_during_exhale = True
                self.start_exhale()
                if hold_active:
                    self.hold_timer.stop()
                self.phase_index = 0
            else:
                if hold_active:
                    self.hold_timer.stop()
                self._maybe_start_phase()

    def _maybe_start_phase(self):
        if not self.pattern:
            return
        if self.phase_index >= len(self.pattern):
            self.phase_index = 0
        expected = self.pattern_states[self.phase_index]
        if expected != self.key_pressed:
            return
        self._start_phase(self.phase_index)

    def _start_phase(self, index: int):
        self.phase_index = index
        phase = self.pattern[index]
        name = phase.get("name", "").lower()
        dur = int(phase.get("duration", 1) * 1000)
        color = self.phase_colors[index]
        if "inh" in name:
            self.start_inhale(color=color, duration=dur)
            try:
                self.animation.finished.disconnect()
            except (TypeError, RuntimeError):
                pass
            self.animation.finished.connect(self._on_phase_animation_finished)
        elif "exh" in name:
            self.start_exhale(color=color, duration=dur)
            try:
                self.animation.finished.disconnect()
            except (TypeError, RuntimeError):
                pass
            self.animation.finished.connect(self._on_phase_animation_finished)
        else:
            # Hold phase
            self.start_hold(color=color, duration=dur)
            return

    def _on_phase_animation_finished(self):
        try:
            self.animation.finished.disconnect()
        except (TypeError, RuntimeError):
            pass
        if self.phase == 'inhaling':
            self.start_ripple()
            if self.inhale_finished_callback:
                self.inhale_finished_callback()
        elif self.phase == 'exhaling':
            if self.cycle_valid:
                exhale_end = time.perf_counter()
                duration = exhale_end - self.breath_start_time
                inhale_dur = self.exhale_start_time - self.inhale_start_time
                exhale_dur = exhale_end - self.exhale_start_time
                self.breath_count += 1
                # Reset flag before callbacks so listeners see final state
                self.released_during_exhale = False
                if self.count_changed_callback:
                    self.count_changed_callback(self.breath_count)
                if self.breath_finished_callback:
                    self.breath_finished_callback(duration, inhale_dur, exhale_dur)
            self.breath_start_time = 0
            self.phase = 'idle'
        self.released_during_exhale = False
        self.phase_index += 1
        if self.phase_index >= len(self.pattern):
            self.phase_index = 0
        expected = self.pattern_states[self.phase_index]
        if expected == self.key_pressed:
            self._start_phase(self.phase_index)
