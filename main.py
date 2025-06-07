from PySide6.QtCore import (Qt, Property, QPropertyAnimation, QEasingCurve,
                            QParallelAnimationGroup, QPointF)
from PySide6.QtGui import QPainter, QBrush, QColor, QFont, QRadialGradient
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                               QMainWindow, QToolButton, QMenu, QHBoxLayout)
import random

class BreathCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._radius = 60
        self.min_radius = 60
        self.max_radius = 140
        self.base_color = QColor(255, 140, 0)      # orange
        # Color used when the circle reaches maximum size (soothing green)
        self.complement_color = QColor(0, 150, 136)
        self._color = self.base_color
        self.inhale_time = 4000  # milliseconds
        self.exhale_time = 6000  # milliseconds
        self.increment = 50      # milliseconds per phase after each cycle
        self.animation = None
        self.offset_animation = None
        self.phase = 'idle'
        self.breath_count = 0
        self.cycle_valid = False
        self.count_changed_callback = None
        self.setMinimumSize(self.max_radius * 2 + 20, self.max_radius * 2 + 20)

        self._offset = QPointF(0, 0)

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

    def getOffset(self):
        return self._offset

    def setOffset(self, value):
        self._offset = value
        self.update()

    offset = Property(QPointF, getOffset, setOffset)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center = self.rect().center()
        g_center = center + self._offset

        gradient = QRadialGradient(g_center, self._radius)
        gradient.setColorAt(0, self._color.lighter(120))
        gradient.setColorAt(1, self._color.darker(150))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, self._radius, self._radius)

    def start_inhale(self):
        if self.phase != 'idle':
            return
        self.phase = 'inhaling'
        self.cycle_valid = False
        self.animate(self._radius, self.max_radius, self.inhale_time,
                     target_color=self.complement_color)
        self.start_texture_animation()

    def start_exhale(self):
        if self.phase != 'inhaling':
            return
        self.cycle_valid = self._radius >= self.max_radius - 1
        self.phase = 'exhaling'
        duration = self.exhale_time if self.cycle_valid else 2000
        self.animate(self._radius, self.min_radius, duration,
                     target_color=self.base_color)
        self.start_texture_animation()

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

    def start_texture_animation(self):
        if self.offset_animation:
            self.offset_animation.stop()
        self.offset_animation = QPropertyAnimation(self, b"offset")
        self.offset_animation.setDuration(2000)
        amp = 8
        new_offset = QPointF(random.uniform(-amp, amp), random.uniform(-amp, amp))
        self.offset_animation.setEndValue(new_offset)
        self.offset_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.offset_animation.finished.connect(self.start_texture_animation)
        self.offset_animation.start()

    def stop_texture_animation(self):
        if self.offset_animation:
            self.offset_animation.stop()

    def animation_finished(self):
        if self.phase == 'exhaling':
            if self.cycle_valid:
                self.breath_count += 1
                if self.count_changed_callback:
                    self.count_changed_callback(self.breath_count)
                self.inhale_time += self.increment
                self.exhale_time += self.increment
            self.phase = 'idle'
            self.stop_texture_animation()
            color_anim = QPropertyAnimation(self, b"color")
            color_anim.setStartValue(self._color)
            color_anim.setEndValue(self.complement_color)
            color_anim.setDuration(800)
            color_anim.setEasingCurve(QEasingCurve.InOutSine)
            color_anim.start()
            self.idle_color_anim = color_anim
        elif self.phase == 'inhaling':
            pass

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calmio")
        self.resize(360, 640)

        self.circle = BreathCircle()
        self.circle.count_changed_callback = self.update_count

        font = QFont()
        font.setFamily("Helvetica")
        font.setPointSize(32)
        font.setBold(True)
        self.label = QLabel("0")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #444;")

        self.menu_button = QToolButton()
        self.menu_button.setText("\u22EE")
        self.menu_button.setStyleSheet(
            "background: transparent; border: none; font-size: 24px; color: #444;"
        )
        self.menu = QMenu()
        self.menu.addAction("Placeholder")
        self.menu_button.setMenu(self.menu)
        self.menu_button.setPopupMode(QToolButton.InstantPopup)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addStretch()
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.circle, alignment=Qt.AlignHCenter)
        layout.addStretch()

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.menu_button)
        layout.addLayout(bottom_layout)

        container = QWidget()
        container.setStyleSheet("background-color: #FAFAFA;")
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setFocusPolicy(Qt.StrongFocus)

    def update_count(self, count):
        self.label.setText(str(count))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.circle.start_inhale()
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.circle.start_exhale()
            event.accept()
        else:
            super().keyReleaseEvent(event)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
