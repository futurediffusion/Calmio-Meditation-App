from PySide6.QtCore import Qt, QEvent, QTimer
from datetime import datetime
import time
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QWidget,
    QPushButton,
)

from .breath_circle import BreathCircle
from .stats_overlay import StatsOverlay


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calmio")
        self.resize(360, 640)

        self.session_active = False
        self.session_start = None
        self.last_cycle_duration = 0

        self.meditation_seconds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.circle = BreathCircle()
        self.circle.count_changed_callback = self.update_count
        self.circle.breath_started_callback = self.on_breath_start
        self.circle.breath_finished_callback = self.on_breath_end

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

        self.menu_button = QPushButton("\u22EF", self)
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.setStyleSheet("background:none; border:none; font-size:24px;")
        self.menu_button.clicked.connect(self.toggle_menu)

        QApplication.instance().installEventFilter(self)

        self.setFocus()

        self.options_button = QPushButton("\u2699\ufe0f", self)
        self.stats_button = QPushButton("\ud83d\udcca", self)
        self.end_button = QPushButton("\U0001F6D1", self)

        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                "QPushButton {background:none; border:none; font-size:20px;}"
            )
            btn.setFocusPolicy(Qt.NoFocus)
            btn.hide()

        self.end_button.clicked.connect(self.end_session)

        self.menu_button.setFocusPolicy(Qt.NoFocus)

        self.stats_overlay = StatsOverlay(self)
        self.stats_overlay.setGeometry(self.rect())
        self.stats_overlay.hide()
        self.stats_button.clicked.connect(self.toggle_stats)

        self.position_buttons()

    def update_count(self, count):
        self.label.setText(str(count))

    def update_timer(self):
        if self.session_active and self.circle.phase != 'idle':
            self.meditation_seconds += 1
            minutes = self.meditation_seconds // 60
            self.stats_overlay.update_minutes(minutes)

    def on_breath_start(self):
        if not self.session_active:
            self.session_active = True
            self.session_start = datetime.now()
        self.cycle_start = time.perf_counter()

    def on_breath_end(self, duration):
        self.last_cycle_duration = int(duration)
        minutes = self.meditation_seconds // 60
        self.stats_overlay.update_minutes(minutes)

    def end_session(self):
        if not self.session_active:
            return
        self.session_active = False
        start_str = self.session_start.strftime("%H:%M") if self.session_start else ""
        minutes = self.meditation_seconds // 60
        breaths = self.circle.breath_count
        self.stats_overlay.update_last_session(start_str, minutes, breaths, self.last_cycle_duration)
        self.stats_overlay.show()
        self.stats_overlay.raise_()

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
        self.end_button.move(x - 3 * (self.menu_button.width() + margin), y)
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
                or self.end_button.geometry().contains(pos)
                or self.stats_overlay.geometry().contains(pos)
            ):
                self.options_button.hide()
                self.stats_button.hide()
                self.end_button.hide()
                self.stats_overlay.hide()
        return super().eventFilter(obj, event)

    def toggle_menu(self):
        if self.options_button.isVisible():
            self.options_button.hide()
            self.stats_button.hide()
            self.end_button.hide()
        else:
            self.options_button.show()
            self.stats_button.show()
            self.end_button.show()

    def toggle_stats(self):
        if self.stats_overlay.isVisible():
            self.stats_overlay.hide()
        else:
            self.stats_overlay.show()
            self.stats_overlay.raise_()

    def mousePressEvent(self, event):
        pos = event.pos()
        if not (
            self.menu_button.geometry().contains(pos)
            or self.options_button.geometry().contains(pos)
            or self.stats_button.geometry().contains(pos)
            or self.end_button.geometry().contains(pos)
            or self.stats_overlay.geometry().contains(pos)
        ):
            self.options_button.hide()
            self.stats_button.hide()
            self.end_button.hide()
            self.stats_overlay.hide()
        super().mousePressEvent(event)
