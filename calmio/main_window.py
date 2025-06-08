from PySide6.QtCore import (
    Qt,
    QEvent,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QSequentialAnimationGroup,
    QVariantAnimation,
    QAbstractAnimation,
)
from datetime import datetime
import json
import time
from pathlib import Path
from PySide6.QtGui import QFont, QFontMetrics, QPalette, QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QWidget,
    QPushButton,
    QStackedWidget,
    QGraphicsOpacityEffect,
)

from .breath_circle import BreathCircle
from .stats_overlay import StatsOverlay
from .session_complete import SessionComplete
from .today_sessions import TodaySessionsView
from .session_details import SessionDetailsView
from .badges_view import BadgesView
from .data_store import DataStore
from .animated_background import AnimatedBackground
from .wave_overlay import WaveOverlay


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calmio")
        self.resize(360, 640)

        palette = QApplication.instance().palette()
        dark_mode = palette.color(QPalette.Window).value() < 128
        self.bg = AnimatedBackground(self, dark_mode=dark_mode)
        self.bg.set_opacity(0.0)
        self.bg.lower()
        self.bg.setGeometry(self.rect())
        self.wave_overlay = WaveOverlay(self)
        self.wave_overlay.setGeometry(self.rect())
        self.wave_overlay.lower()

        self.data_store = DataStore()

        self.session_active = False
        self.session_start = None
        self.last_cycle_duration = 0
        self.last_inhale = 0
        self.last_exhale = 0
        self.cycle_durations = []

        self.meditation_seconds = self.data_store.get_today_seconds()
        self.session_seconds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.circle = BreathCircle()
        self.circle.count_changed_callback = self.update_count
        self.circle.breath_started_callback = self.on_breath_start
        self.circle.breath_finished_callback = self.on_breath_end
        self.circle.exhale_started_callback = self.on_exhale_start
        self.circle.ripple_spawned_callback = self.start_waves

        font = QFont("Sans Serif")
        font.setPointSize(32)
        font.setBold(True)
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)
        self.label.setStyleSheet("color:white;")
        self.base_text_color = QColor("white")
        self.active_text_color = self.circle.complement_color
        self.text_color_anim = None
        self.count_opacity = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.count_opacity)
        self.count_opacity.setOpacity(0)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addStretch()
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.circle, alignment=Qt.AlignHCenter)

        msg_font = QFont("Sans Serif")
        msg_font.setPointSize(14)
        self.message_label = QLabel("Toca para comenzar")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setFont(msg_font)
        self.message_label.setStyleSheet("color:#000000;")
        self.message_label.setWordWrap(True)
        self.message_label.setVisible(False)
        self.message_container = QWidget()
        msg_layout = QVBoxLayout(self.message_container)
        msg_layout.setContentsMargins(0, 0, 0, 0)
        msg_layout.setSpacing(0)
        msg_layout.addWidget(self.message_label, alignment=Qt.AlignCenter)
        # Reserve height for the largest animation size so layout doesn't move
        max_font = QFont(msg_font)
        max_font.setPointSize(18)
        fm = QFontMetrics(max_font)
        # Allow up to three lines of text while keeping layout stable
        self.message_container.setFixedHeight(fm.height() * 3)
        # Keep container visible so layout doesn't shift when messages appear
        self.message_container.setVisible(True)
        layout.addWidget(self.message_container, alignment=Qt.AlignHCenter)

        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.main_view = container

        self.session_complete = SessionComplete(self)
        self.session_complete.done.connect(self.on_session_complete_done)
        self.session_complete.closed.connect(self.on_session_complete_closed)
        self.session_complete.badges_requested.connect(
            lambda badges: self.open_session_badges(badges, return_to=self.session_complete)
        )

        self.stack = QStackedWidget()
        self.stack.addWidget(self.main_view)
        self.stack.addWidget(self.session_complete)
        self.wave_overlay.stackUnder(self.stack)

        self.setCentralWidget(self.stack)
        self.setFocusPolicy(Qt.StrongFocus)

        self.menu_button = QPushButton("\u22EF", self)
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.setStyleSheet(
            "background:none; border:none; font-size:24px; color:#000;"
        )
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
        self.stats_overlay.view_sessions.connect(self.open_today_sessions)
        self.stats_overlay.session_requested.connect(self.open_session_details)
        self.stats_overlay.view_badges_today.connect(self.open_today_badges)

        self.today_sessions = TodaySessionsView(self)
        self.today_sessions.setGeometry(self.rect())
        self.today_sessions.hide()
        self.today_sessions.back_requested.connect(self.close_today_sessions)
        self.today_sessions.session_selected.connect(self.open_session_details)

        self.session_details = SessionDetailsView(self)
        self.session_details.setGeometry(self.rect())
        self.session_details.hide()
        self.session_details.back_requested.connect(self.close_session_details)
        self.session_details.badges_requested.connect(self.open_session_badges)

        self.badges_view = BadgesView(self)
        self.badges_view.setGeometry(self.rect())
        self.badges_view.hide()
        self.badges_view.back_requested.connect(self.close_badges_view)
        self._badges_return = self.stats_overlay

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
                last.get("cycles", []),
            )
        self.stats_overlay.update_streak(self.data_store.get_streak())
        self.stats_overlay.update_badges(
            self.data_store.get_badges_for_date(datetime.now())
        )

        self.position_buttons()

        self.load_messages()
        self.build_message_schedule()
        self.message_index = 0
        self.msg_opacity = QGraphicsOpacityEffect(self.message_label)
        self.message_label.setGraphicsEffect(self.msg_opacity)
        self.start_prompt_animation()

    def update_count(self, count):
        """Handle breath count updates after a full cycle."""
        self.check_motivational_message(count)

    def update_timer(self):
        if self.session_active and self.circle.phase != 'idle':
            self.meditation_seconds += 1
            self.session_seconds += 1
            self.stats_overlay.update_minutes(self.meditation_seconds)

    def start_waves(self, center, color):
        if hasattr(self, "wave_overlay"):
            self.wave_overlay.start_waves(center, color)

    def on_breath_start(self):
        if not self.session_active:
            self.session_active = True
            self.session_start = datetime.now()
            self.session_seconds = 0
            self.cycle_durations = []
            self.stop_prompt_animation()
        self.cycle_start = time.perf_counter()

        if (
            hasattr(self, "count_anim")
            and self.count_anim.state() != QAbstractAnimation.Stopped
        ):
            self.count_anim.stop()

        self.label.setText(str(self.circle.breath_count + 1))
        self.count_opacity.setOpacity(0)
        self.count_anim = QPropertyAnimation(self.count_opacity, b"opacity", self)
        self.count_anim.setDuration(int(self.circle.inhale_time))
        self.count_anim.setStartValue(0)
        self.count_anim.setEndValue(1)
        self.count_anim.start()

        if self.text_color_anim and self.text_color_anim.state() != QAbstractAnimation.Stopped:
            self.text_color_anim.stop()
        self.text_color_anim = QVariantAnimation(self)
        self.text_color_anim.setDuration(int(self.circle.inhale_time))
        self.text_color_anim.setStartValue(self.base_text_color)
        self.text_color_anim.setEndValue(self.active_text_color)
        self.text_color_anim.valueChanged.connect(self._update_label_color)
        self.text_color_anim.start()

        if hasattr(self, "bg_anim") and self.bg_anim.state() != QAbstractAnimation.Stopped:
            self.bg_anim.stop()
        self.bg_anim = QPropertyAnimation(self.bg, b"opacity", self)
        self.bg_anim.setDuration(int(self.circle.inhale_time))
        self.bg_anim.setStartValue(self.bg.opacity)
        self.bg_anim.setEndValue(1.0)
        self.bg_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.bg_anim.start()

    def on_exhale_start(self, duration):
        if (
            hasattr(self, "count_anim")
            and self.count_anim.state() != QAbstractAnimation.Stopped
        ):
            self.count_anim.stop()

        self.count_anim = QPropertyAnimation(self.count_opacity, b"opacity", self)
        self.count_anim.setDuration(int(duration))
        self.count_anim.setStartValue(self.count_opacity.opacity())
        self.count_anim.setEndValue(0)
        self.count_anim.start()

        if self.text_color_anim and self.text_color_anim.state() != QAbstractAnimation.Stopped:
            self.text_color_anim.stop()
        self.text_color_anim = QVariantAnimation(self)
        self.text_color_anim.setDuration(int(duration))
        self.text_color_anim.setStartValue(self.active_text_color)
        self.text_color_anim.setEndValue(self.base_text_color)
        self.text_color_anim.valueChanged.connect(self._update_label_color)
        self.text_color_anim.start()

        if hasattr(self, "bg_anim") and self.bg_anim.state() != QAbstractAnimation.Stopped:
            self.bg_anim.stop()
        self.bg_anim = QPropertyAnimation(self.bg, b"opacity", self)
        self.bg_anim.setDuration(int(duration))
        self.bg_anim.setStartValue(self.bg.opacity)
        self.bg_anim.setEndValue(0.0)
        self.bg_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.bg_anim.start()

    def on_breath_end(self, duration, inhale, exhale):
        self.last_cycle_duration = duration
        self.last_inhale = inhale
        self.last_exhale = exhale
        self.cycle_durations.append({"inhale": inhale, "exhale": exhale})
        self.stats_overlay.update_minutes(self.meditation_seconds)

    def end_session(self):
        if not self.session_active:
            return
        self.session_active = False
        start_str = self.session_start.strftime("%H:%M:%S") if self.session_start else ""
        duration_seconds = self.session_seconds
        breaths = self.circle.breath_count
        new_badges = self.data_store.add_session(
            self.session_start,
            duration_seconds,
            breaths,
            self.last_inhale,
            self.last_exhale,
            self.cycle_durations,
        )
        self.stats_overlay.update_last_session(
            start_str,
            duration_seconds,
            breaths,
            self.last_inhale,
            self.last_exhale,
            self.cycle_durations,
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
        if new_badges:
            self.session_complete.show_badges(new_badges)
        else:
            self.session_complete.show_badges([])
        self.stack.setCurrentWidget(self.session_complete)
        self.stats_overlay.update_streak(self.data_store.get_streak())
        self.stats_overlay.update_badges(
            self.data_store.get_badges_for_date(datetime.now())
        )
        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.hide()

        if hasattr(self, "bg_anim") and self.bg_anim.state() != QAbstractAnimation.Stopped:
            self.bg_anim.stop()
        self.bg_anim = QPropertyAnimation(self.bg, b"opacity", self)
        self.bg_anim.setDuration(1000)
        self.bg_anim.setStartValue(self.bg.opacity)
        self.bg_anim.setEndValue(0.0)
        self.bg_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.bg_anim.start()

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
        self.today_sessions.setGeometry(self.rect())
        self.session_details.setGeometry(self.rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_buttons()
        if hasattr(self, "bg"):
            self.bg.setGeometry(self.rect())
        if hasattr(self, "wave_overlay"):
            self.wave_overlay.setGeometry(self.rect())

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
                or self.today_sessions.geometry().contains(pos)
                or self.session_details.geometry().contains(pos)
                or self.badges_view.geometry().contains(pos)
            ):
                self.options_button.hide()
                self.stats_button.hide()
                self.end_button.hide()
                self.stats_overlay.hide()
                self.today_sessions.hide()
                self.session_details.hide()
                self.badges_view.hide()
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
            self.today_sessions.hide()
            self.session_details.hide()
        else:
            self.today_sessions.hide()
            self.session_details.hide()
            self.stats_overlay.show()
            self.stats_overlay.raise_()

    def close_stats(self):
        self.stats_overlay.hide()
        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.hide()

    def open_today_sessions(self):
        sessions = self.data_store.get_sessions_for_date(datetime.now())
        self.today_sessions.set_sessions(sessions)
        self.stats_overlay.hide()
        self.session_details.hide()
        self.today_sessions.show()
        self.today_sessions.raise_()

    def close_today_sessions(self):
        self.today_sessions.hide()
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
            or self.today_sessions.geometry().contains(pos)
            or self.session_details.geometry().contains(pos)
            or self.badges_view.geometry().contains(pos)
        ):
            self.options_button.hide()
            self.stats_button.hide()
            self.end_button.hide()
            self.stats_overlay.hide()
            self.today_sessions.hide()
            self.session_details.hide()
            self.badges_view.hide()
        super().mousePressEvent(event)

    def on_session_complete_done(self):
        self.stack.setCurrentWidget(self.main_view)
        self.stats_overlay.show()
        self.stats_overlay.raise_()
        self.circle.breath_count = 0
        self.label.setText("")
        self.count_opacity.setOpacity(0)
        self.session_seconds = 0
        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.hide()
        self.start_prompt_animation()

    def on_session_complete_closed(self):
        self.stack.setCurrentWidget(self.main_view)
        self.circle.breath_count = 0
        self.label.setText("")
        self.count_opacity.setOpacity(0)
        self.session_seconds = 0
        for btn in (self.options_button, self.stats_button, self.end_button):
            btn.hide()
        self.start_prompt_animation()

    def open_session_details(self, session):
        is_last = False
        try:
            is_last = session == self.data_store.get_last_session()
        except Exception:
            pass
        self.session_details.set_session(session, is_last=is_last)
        self.stats_overlay.hide()
        self.today_sessions.hide()
        self.session_details.show()
        self.session_details.raise_()

    def close_session_details(self):
        self.session_details.hide()
        self.stats_overlay.show()
        self.stats_overlay.raise_()

    def open_today_badges(self):
        badges = self.data_store.get_badges_for_date(datetime.now())
        self.badges_view.title_lbl.setText("Logros de hoy")
        self.badges_view.set_badges(badges)
        self._badges_return = self.stats_overlay
        self.stats_overlay.hide()
        self.badges_view.show()
        self.badges_view.raise_()

    def open_session_badges(self, badges, return_to=None):
        self.badges_view.title_lbl.setText("Logros de sesi\u00f3n")
        self.badges_view.set_badges(badges)
        if return_to is None:
            return_to = self.session_details
        self._badges_return = return_to
        return_to.hide()
        self.badges_view.show()
        self.badges_view.raise_()

    def close_badges_view(self):
        self.badges_view.hide()
        if self._badges_return:
            self._badges_return.show()
            self._badges_return.raise_()

    def load_messages(self):
        path = Path(__file__).resolve().parent / "motivational_messages.json"
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.motivational_messages = data.get("messages", [])
        except Exception:
            self.motivational_messages = []

    def build_message_schedule(self, max_count: int = 150):
        """Generate an increasing interval schedule for motivational messages."""
        schedule = []
        interval = 3
        total = 0
        while total < max_count:
            for _ in range(3):
                total += interval
                schedule.append(total)
            interval += 1
        self.message_schedule = set(schedule)

    def start_prompt_animation(self):
        self.message_label.setText("Toca para comenzar")
        self.message_label.show()
        self.message_container.show()
        self.msg_opacity.setOpacity(0.2)
        self.fade_anim = QPropertyAnimation(self.msg_opacity, b"opacity", self)
        self.fade_anim.setDuration(1500)
        self.fade_anim.setStartValue(0.2)
        self.fade_anim.setKeyValueAt(0.5, 1)
        self.fade_anim.setEndValue(0.2)
        self.fade_anim.setLoopCount(-1)
        self.fade_anim.start()

        self.bounce_anim = QVariantAnimation(self)
        self.bounce_anim.setDuration(3000)
        self.bounce_anim.setStartValue(14)
        self.bounce_anim.setKeyValueAt(0.5, 18)
        self.bounce_anim.setEndValue(14)
        self.bounce_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.bounce_anim.setLoopCount(-1)
        self.bounce_anim.valueChanged.connect(self._update_message_font)
        self.bounce_anim.start()

    def _update_message_font(self, value):
        font = self.message_label.font()
        font.setPointSize(int(value))
        self.message_label.setFont(font)

    def _update_label_color(self, color):
        if isinstance(color, QColor):
            self.label.setStyleSheet(f"color:{color.name()};")

    def stop_prompt_animation(self):
        if hasattr(self, "fade_anim"):
            self.fade_anim.stop()
        if hasattr(self, "bounce_anim"):
            self.bounce_anim.stop()
        hide = QPropertyAnimation(self.msg_opacity, b"opacity", self)
        hide.setDuration(4000)
        hide.setStartValue(self.msg_opacity.opacity())
        hide.setEndValue(0)
        hide.finished.connect(self.message_label.hide)
        hide.start()
        self.fade_anim = hide

    def display_motivational_message(self, text):
        self.msg_opacity.setOpacity(0)
        self.message_label.setText(text)
        self.message_label.show()
        fade_in = QPropertyAnimation(self.msg_opacity, b"opacity", self)
        fade_in.setDuration(600)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_out = QPropertyAnimation(self.msg_opacity, b"opacity", self)
        fade_out.setDuration(4000)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        group = QSequentialAnimationGroup(self)
        group.addAnimation(fade_in)
        group.addPause(1000)
        group.addAnimation(fade_out)
        group.finished.connect(self.message_label.hide)
        group.start()
        self.temp_msg_anim = group

    def check_motivational_message(self, count):
        if count in self.message_schedule and self.motivational_messages:
            msg = self.motivational_messages[self.message_index % len(self.motivational_messages)]
            self.message_index += 1
            self.display_motivational_message(msg)
