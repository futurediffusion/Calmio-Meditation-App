from PySide6.QtCore import (
    Qt,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QEvent,
    QTimer,
)
from PySide6.QtGui import QPainter, QBrush, QColor, QFont, QRadialGradient, QPen
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
)

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
        self.phase = 'idle'
        self.breath_count = 0
        self.cycle_valid = False
        self.count_changed_callback = None
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center = self.rect().center()

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
        self.cycle_valid = False
        self.animate(self._radius, self.max_radius, self.inhale_time,
                     target_color=self.complement_color)

    def start_exhale(self):
        if self.phase != 'inhaling':
            return
        self.cycle_valid = self._radius >= self.max_radius - 1
        self.phase = 'exhaling'
        duration = self.exhale_time if self.cycle_valid else 2000
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

    def animation_finished(self):
        if self.phase == 'exhaling':
            if self.cycle_valid:
                self.breath_count += 1
                if self.count_changed_callback:
                    self.count_changed_callback(self.breath_count)
                self.inhale_time += self.increment
                self.exhale_time += self.increment
            self.phase = 'idle'
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

class ProgressCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.minutes = 0
        self.goal_step = 30
        self.setMinimumSize(220, 220)

    def set_minutes(self, m):
        self.minutes = m
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(20, 20, -20, -20)

        base_pen = QPen(QColor(200, 220, 255), 12, Qt.SolidLine, Qt.RoundCap)
        progress_pen = QPen(QColor(255, 204, 188), 12, Qt.SolidLine, Qt.RoundCap)

        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)

        progress = (self.minutes % self.goal_step) / self.goal_step
        painter.setPen(progress_pen)
        painter.drawArc(rect, 90 * 16, int(-360 * 16 * progress))

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.NoBrush)

        # Center text
        font = QFont("Sans Serif")
        font.setPointSize(14)
        painter.setFont(font)
        painter.setPen(QColor("#444"))
        center_text = f"{self.minutes} min\nmeditated"
        painter.drawText(self.rect(), Qt.AlignCenter, center_text)

        # Labels
        base = (self.minutes // self.goal_step) * self.goal_step
        labels = {
            "top": base + self.goal_step,
            "right": base + 10,
            "left": base + 20,
        }

        label_font = QFont("Sans Serif")
        label_font.setPointSize(10)
        painter.setFont(label_font)
        painter.drawText(
            rect.center().x() - 10,
            rect.top() - 5,
            f"{labels['top']} min",
        )
        painter.drawText(
            rect.right() - 40,
            rect.bottom() + 15,
            f"{labels['right']} min",
        )
        painter.drawText(
            rect.left() + 10,
            rect.bottom() + 15,
            f"{labels['left']} min",
        )


class StatsOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color:#FAFAFA; border-radius:20px;"
            "color:#444;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Today's Meditation", self)
        title_font = QFont("Sans Serif")
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)

        self.progress = ProgressCircle(self)

        layout.addWidget(title)
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)

    def update_minutes(self, m):
        self.progress.set_minutes(m)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calmio")
        self.resize(360, 640)

        self.meditation_seconds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.circle = BreathCircle()
        self.circle.count_changed_callback = self.update_count

        font = QFont("Sans Serif")
        font.setPointSize(32)
        font.setBold(True)
        self.label = QLabel("0")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addStretch()
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.circle, alignment=Qt.AlignHCenter)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setFocusPolicy(Qt.StrongFocus)

        # Floating menu buttons
        self.menu_button = QPushButton("\u22EF", self)  # "⋯" icon
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.setStyleSheet("background:none; border:none; font-size:24px;")
        self.menu_button.clicked.connect(self.toggle_menu)

        QApplication.instance().installEventFilter(self)

        self.setFocus()

        self.options_button = QPushButton("\u2699\ufe0f", self)  # "⚙️" icon
        self.stats_button = QPushButton("\ud83d\udcca", self)    # "📊" icon

        for btn in (self.options_button, self.stats_button):
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                "QPushButton {background:none; border:none; font-size:20px;}"
            )
            btn.setFocusPolicy(Qt.NoFocus)
            btn.hide()

        self.menu_button.setFocusPolicy(Qt.NoFocus)

        self.stats_overlay = StatsOverlay(self)
        self.stats_overlay.setGeometry(self.rect())
        self.stats_overlay.hide()
        self.stats_button.clicked.connect(self.toggle_stats)

        self.position_buttons()

    def update_count(self, count):
        self.label.setText(str(count))

    def update_timer(self):
        if self.circle.phase != 'idle':
            self.meditation_seconds += 1
            minutes = self.meditation_seconds // 60
            self.stats_overlay.update_minutes(minutes)

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

    def position_buttons(self):
        margin = 10
        x = self.width() - self.menu_button.width() - margin
        y = self.height() - self.menu_button.height() - margin
        self.menu_button.move(x, y)
        self.options_button.move(x - self.options_button.width() - margin, y)
        self.stats_button.move(x - 2 * (self.menu_button.width() + margin), y)
        self.stats_overlay.setGeometry(self.rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_buttons()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            pos = self.mapFromGlobal(event.globalPosition().toPoint())
            if not (
                self.menu_button.geometry().contains(pos)
                or self.options_button.geometry().contains(pos)
                or self.stats_button.geometry().contains(pos)
                or self.stats_overlay.geometry().contains(pos)
            ):
                self.options_button.hide()
                self.stats_button.hide()
                self.stats_overlay.hide()
        return super().eventFilter(obj, event)

    def toggle_menu(self):
        if self.options_button.isVisible():
            self.options_button.hide()
            self.stats_button.hide()
        else:
            self.options_button.show()
            self.stats_button.show()

    def toggle_stats(self):
        if self.stats_overlay.isVisible():
            self.stats_overlay.hide()
        else:
            self.stats_overlay.show()
            self.stats_overlay.raise_()

    def mousePressEvent(self, event):
        pos = event.pos()
        if not (self.menu_button.geometry().contains(pos) or
                self.options_button.geometry().contains(pos) or
                self.stats_button.geometry().contains(pos) or
                self.stats_overlay.geometry().contains(pos)):
            self.options_button.hide()
            self.stats_button.hide()
            self.stats_overlay.hide()
        super().mousePressEvent(event)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
