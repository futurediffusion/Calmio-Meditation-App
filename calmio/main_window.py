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
    QStackedWidget,
)

from .breath_circle import BreathCircle
from .stats_overlay import StatsOverlay
from .session_complete import SessionComplete
from .data_store import DataStore


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calmio")
        self.resize(360, 640)

        self.data_store = DataStore()

        self.session_active = False
        self.session_start = None
        self.last_cycle_duration = 0
        self.last_inhale = 0
        self.last_exhale = 0

        self.meditation_seconds = self.data_store.get_today_seconds()
        self.session_seconds = 0
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
        self.main_view = container

        self.session_complete = SessionComplete(self)
        self.session_complete.done.connect(self.on_session_complete_done)
        self.session_complete.closed.connect(self.on_session_complete_closed)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.main_view)
        self.stack.addWidget(self.session_complete)

        self.setCentralWidget(self.stack)
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

        # Initialize overlay with stored data
        self.stats_overlay.update_minutes(self.meditation_seconds)
        last = self.data_store.get_last_session()
        if last:
            time_part = last.get("start", "").split(" ")[-1] if last.get("start") else ""
            self.stats_overlay.update_last_session(
                time_part,
                last.get("duration", 0),
                last.get("breaths", 0),
                last.get("last_inhale", 0),
                last.get("last_exhale", 0),
            )
        self.stats_overlay.update_streak(self.data_store.get_streak())

        self.position_buttons()

    def update_count(self, count):
        self.label.setText(str(count))

    def update_timer(self):
        if self.session_active and self.circle.phase != 'idle':
            self.meditation_seconds += 1
            self.session_seconds += 1
            self.stats_overlay.update_minutes(self.meditation_seconds)

    def on_breath_start(self):
        if not self.session_active:
            self.session_active = True
            self.session_start = datetime.now()
            self.session_seconds = 0
        self.cycle_start = time.perf_counter()

    def on_breath_end(self, duration, inhale, exhale):
        self.last_cycle_duration = duration
        self.last_inhale = inhale
        self.last_exhale = exhale
        self.stats_overlay.update_minutes(self.meditation_seconds)

    def end_session(self):
        if not self.session_active:
            return
        self.session_active = False
        start_str = self.session_start.strftime("%H:%M:%S") if self.session_start else ""
        duration_seconds = self.session_seconds
        breaths = self.circle.breath_count
        self.data_store.add_session(
            self.session_start, duration_seconds, breaths, self.last_inhale, self.last_exhale
        )
        self.stats_overlay.update_last_session(
            start_str, duration_seconds, breaths, self.last_inhale, self.last_exhale
        )
        self.stats_overlay.update_minutes(self.meditation_seconds)

        end_time_str = datetime.now().strftime("%I:%M %p")
        start_time_str = self.session_start.strftime("%I:%M %p")
        self.session_complete.set_stats(
            duration_seconds,
            breaths,
            self.last_inhale,
            self.last_exhale,
            start_time_str,
            end_time_str,
        )
        self.stack.setCurrentWidget(self.session_complete)
        self.stats_overlay.update_streak(self.data_store.get_streak())
        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.hide()

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
            if hasattr(event, "globalPosition"):
                pos = self.mapFromGlobal(event.globalPosition().toPoint())
            else:
                pos = self.mapFromGlobal(event.globalPos())
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

    def close_stats(self):
        self.stats_overlay.hide()
        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.hide()

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

    def on_session_complete_done(self):
        self.stack.setCurrentWidget(self.main_view)
        self.stats_overlay.show()
        self.stats_overlay.raise_()
        self.circle.breath_count = 0
        self.label.setText("0")
        self.session_seconds = 0
        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.hide()

    def on_session_complete_closed(self):
        self.stack.setCurrentWidget(self.main_view)
        self.circle.breath_count = 0
        self.label.setText("0")
        self.session_seconds = 0
        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.hide()
