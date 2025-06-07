from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QBrush, QColor, QFont
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow

class BreathCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._radius = 60
        self.min_radius = 60
        self.max_radius = 140
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 140, 0)))  # orange
        painter.setPen(Qt.NoPen)
        center = self.rect().center()
        painter.drawEllipse(center, self._radius, self._radius)

    def start_inhale(self):
        if self.phase != 'idle':
            return
        self.phase = 'inhaling'
        self.cycle_valid = False
        self.animate(self._radius, self.max_radius, self.inhale_time)

    def start_exhale(self):
        if self.phase != 'inhaling':
            return
        self.cycle_valid = self._radius >= self.max_radius - 1
        self.phase = 'exhaling'
        duration = self.exhale_time if self.cycle_valid else 2000
        self.animate(self._radius, self.min_radius, duration)

    def animate(self, start, end, duration):
        if self.animation:
            self.animation.stop()
        self.animation = QPropertyAnimation(self, b"radius")
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.setDuration(int(duration))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
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
            # Wait for release to exhale
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
