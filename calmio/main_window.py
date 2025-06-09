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
import random
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
from .options_overlay import OptionsOverlay
from .developer_overlay import DeveloperOverlay
from .sound_overlay import SoundOverlay
from .breath_modes_overlay import BreathModesOverlay
from .data_store import DataStore
from .animated_background import AnimatedBackground
from .wave_overlay import WaveOverlay
from .menu_handler import MenuHandler
from .session_manager import SessionManager
from .overlay_manager import OverlayManager
from .message_utils import MessageHandler
from .sound_manager import SoundManager
from .biofeedback_overlay import BioFeedbackOverlay


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
        self.speed_multiplier = 1
        self.timer = QTimer(self)
        # Handlers
        self.session_manager = SessionManager(self)
        self.menu_handler = MenuHandler(self)
        self.overlay_manager = OverlayManager(self)
        self.message_handler = MessageHandler(self)
        self.sound_manager = SoundManager(self)
        self.current_pattern_id = None

        self.biofeedback_messages = []
        self._load_biofeedback_messages()

        self.timer.timeout.connect(self.session_manager.update_timer)
        self.timer.start(1000)

        self._chakra_index = 0

        self.circle = BreathCircle()
        self.circle.count_changed_callback = self.update_count
        self.circle.breath_started_callback = self.session_manager.on_breath_start
        self.circle.breath_finished_callback = self.session_manager.on_breath_end
        self.circle.exhale_started_callback = self.session_manager.on_exhale_start
        self.circle.hold_started_callback = self.session_manager.on_hold_start
        self.circle.ripple_spawned_callback = self.session_manager.start_waves
        self.circle.inhale_finished_callback = self.on_inhale_finished
        self.update_speed()

        font = QFont("Sans Serif")
        font.setPointSize(32)
        font.setBold(True)
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)
        self.label.setStyleSheet("color:white;")
        self.base_text_color = QColor("white")
        self.active_text_color = self.circle.complement_color
        self.current_text_color = self.base_text_color
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
        self.session_complete.done.connect(self.overlay_manager.on_session_complete_done)
        self.session_complete.closed.connect(self.overlay_manager.on_session_complete_closed)
        self.session_complete.badges_requested.connect(
            lambda badges: self.overlay_manager.open_session_badges(badges, return_to=self.session_complete)
        )

        self.biofeedback_overlay = BioFeedbackOverlay(self)
        self.biofeedback_overlay.setGeometry(self.rect())
        self.biofeedback_overlay.hide()
        self.biofeedback_overlay.done.connect(self.display_session_complete)

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
        self.dev_button = QPushButton("\U0001F41B", self)
        self.sound_button = QPushButton("\U0001F3B5", self)
        self.patterns_button = QPushButton("\U0001FAC2", self)

        self.control_buttons = [
            self.options_button,
            self.stats_button,
            self.end_button,
            self.dev_button,
            self.sound_button,
            self.patterns_button,
        ]
        for btn in self.control_buttons:
            self._setup_control_button(btn)

        self.end_button.clicked.connect(self.session_manager.end_session)

        self.menu_button.setFocusPolicy(Qt.NoFocus)

        self.stats_overlay = StatsOverlay(self)
        self.stats_overlay.setGeometry(self.rect())
        self.stats_overlay.hide()
        self.stats_button.clicked.connect(self.overlay_manager.toggle_stats)
        self.stats_overlay.view_sessions.connect(self.overlay_manager.open_today_sessions)
        self.stats_overlay.session_requested.connect(self.overlay_manager.open_session_details)
        self.stats_overlay.view_badges_today.connect(self.overlay_manager.open_today_badges)

        self.today_sessions = TodaySessionsView(self)
        self.today_sessions.setGeometry(self.rect())
        self.today_sessions.hide()
        self.today_sessions.back_requested.connect(self.overlay_manager.close_today_sessions)
        self.today_sessions.session_selected.connect(self.overlay_manager.open_session_details)

        self.session_details = SessionDetailsView(self)
        self.session_details.setGeometry(self.rect())
        self.session_details.hide()
        self.session_details.back_requested.connect(self.overlay_manager.close_session_details)
        self.session_details.badges_requested.connect(self.overlay_manager.open_session_badges)

        self.badges_view = BadgesView(self)
        self.badges_view.setGeometry(self.rect())
        self.badges_view.hide()
        self.badges_view.back_requested.connect(self.overlay_manager.close_badges_view)
        self._badges_return = self.stats_overlay

        self.options_overlay = OptionsOverlay(self)
        self.options_overlay.setGeometry(self.rect())
        self.options_overlay.hide()
        self.options_overlay.back_requested.connect(self.menu_handler.close_options)
        self.options_button.clicked.connect(self.menu_handler.toggle_options)
        self.dev_menu = DeveloperOverlay(self)
        self.dev_menu.hide()
        self.dev_menu.speed_toggled.connect(self.session_manager.toggle_developer_speed)
        self.dev_menu.next_day_requested.connect(self.session_manager.advance_day)
        self.dev_button.clicked.connect(self.menu_handler.toggle_developer_menu)

        self.sound_overlay = SoundOverlay(self)
        self.sound_overlay.setGeometry(self.rect())
        self.sound_overlay.hide()
        self.sound_overlay.back_requested.connect(self.menu_handler.close_sound)
        self.sound_overlay.environment_changed.connect(self.sound_manager.set_environment)
        self.sound_overlay.music_toggled.connect(self.sound_manager.set_music_enabled)
        self.sound_overlay.bell_toggled.connect(self.sound_manager.set_bell_enabled)
        self.sound_overlay.volume_changed.connect(self.sound_manager.set_volume)
        self.sound_overlay.bell_volume_changed.connect(self.sound_manager.set_bell_volume)
        self.sound_overlay.music_volume_changed.connect(self.sound_manager.set_music_volume)
        self.sound_overlay.drop_volume_changed.connect(self.sound_manager.set_drop_volume)
        self.sound_overlay.mute_all.connect(self.sound_manager.mute_all)
        self.sound_overlay.music_mode_changed.connect(self.sound_manager.set_music_mode)
        self.sound_overlay.scale_changed.connect(self.sound_manager.set_scale_type)
        self.sound_overlay.breath_volume_toggled.connect(self.sound_manager.set_breath_volume_enabled)
        self.sound_button.clicked.connect(self.menu_handler.toggle_sound)

        self.breath_modes = BreathModesOverlay(self)
        self.breath_modes.setGeometry(self.rect())
        self.breath_modes.hide()
        self.breath_modes.back_requested.connect(self.menu_handler.close_breath_modes)
        self.breath_modes.pattern_selected.connect(self._on_pattern_selected)
        self.patterns_button.clicked.connect(self.menu_handler.toggle_breath_modes)

        music_enabled = self.data_store.get_sound_setting("music_enabled", False)
        bell_enabled = self.data_store.get_sound_setting("bell_enabled", False)
        breath_volume = self.data_store.get_sound_setting("breath_volume", False)
        self.sound_overlay.music_chk.setChecked(music_enabled)
        self.sound_overlay.bell_chk.setChecked(bell_enabled)
        self.sound_overlay.set_breath_volume(breath_volume)
        mode = self.data_store.get_sound_setting("music_mode", "scale")
        scale = self.data_store.get_sound_setting("scale_type", "major")
        self.sound_overlay.set_music_mode(mode)
        self.sound_overlay.set_scale_type(scale)
        self.sound_manager.set_music_mode(mode)
        self.sound_manager.set_scale_type(scale)
        self.sound_manager.set_music_enabled(music_enabled)
        self.sound_manager.set_bell_enabled(bell_enabled)
        self.sound_manager.set_breath_volume_enabled(breath_volume)
        self.sound_overlay.music_toggled.connect(
            lambda v: self.data_store.set_sound_setting("music_enabled", v)
        )
        self.sound_overlay.bell_toggled.connect(
            lambda v: self.data_store.set_sound_setting("bell_enabled", v)
        )
        self.sound_overlay.music_mode_changed.connect(
            lambda v: self.data_store.set_sound_setting("music_mode", v)
        )
        self.sound_overlay.scale_changed.connect(
            lambda v: self.data_store.set_sound_setting("scale_type", v)
        )
        self.sound_overlay.breath_volume_toggled.connect(
            lambda v: self.data_store.set_sound_setting("breath_volume", v)
        )

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
            self.data_store.get_badges_for_date(self.data_store.now())
        )

        self.menu_handler.position_buttons()

        self.message_handler.load_messages()
        self.message_handler.build_message_schedule()
        self.message_handler.message_index = 0
        self.msg_opacity = QGraphicsOpacityEffect(self.message_label)
        self.message_label.setGraphicsEffect(self.msg_opacity)
        self.message_handler.start_prompt_animation()

    def update_count(self, count):
        """Handle breath count updates after a full cycle."""
        self.check_motivational_message(count)
        if hasattr(self, "sound_manager"):
            play_music = True
            if self.current_pattern_id == "triple":
                # Only play a note after completing three full breaths
                play_music = (
                    count % 3 == 0 and not self.circle.released_during_exhale
                )
            elif self.current_pattern_id == "box":
                # For box breathing the note is triggered when the final hold
                # ends, so don't play it here on exhale completion
                play_music = False
            elif self.circle.released_during_exhale:
                play_music = False
            if play_music:
                self.sound_manager.maybe_play_music(count)
            self.circle.released_during_exhale = False
        index = self._chakra_index_for_count(count)
        if getattr(self, "_chakra_index", None) != index:
            self._chakra_index = index
            self.bg.transition_to_index(index)

    def _chakra_index_for_count(self, count: int) -> int:
        """Return chakra index for the given breath count within the 30-cycle."""
        count = ((count - 1) % 30) + 1
        thresholds = [4, 8, 12, 16, 20, 25, 30]
        for i, t in enumerate(thresholds):
            if count <= t:
                return i
        return 0

    def update_timer(self):
        self.session_manager.update_timer()

    def start_waves(self, center, color):
        self.session_manager.start_waves(center, color)

    def on_breath_start(self, color, duration):
        self.session_manager.on_breath_start(color, duration)

    def on_exhale_start(self, duration, color):
        self.session_manager.on_exhale_start(duration, color)

    def on_hold_start(self, duration, color):
        self.session_manager.on_hold_start(duration, color)

    def on_inhale_finished(self):
        """Handle actions when a breathing phase ends."""
        # During box breathing play the musical note when the last hold
        # completes instead of the usual drop cue.
        if (
            self.current_pattern_id == "box"
            and self.circle.phase == "holding"
            and self.circle.pattern
            and self.circle.phase_index == len(self.circle.pattern) - 1
        ):
            self.sound_manager.maybe_play_music(self.circle.breath_count)
        else:
            self.sound_manager.play_drop()
            self.sound_manager.maybe_play_bell(self.circle.breath_count + 1)

    def on_breath_end(self, duration, inhale, exhale):
        self.session_manager.on_breath_end(duration, inhale, exhale)

    def end_session(self):
        self.session_manager.end_session()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.circle.on_press()
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.circle.on_release()
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def position_buttons(self):
        self.menu_handler.position_buttons()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.menu_handler.position_buttons()
        if hasattr(self, "bg"):
            self.bg.setGeometry(self.rect())
        if hasattr(self, "wave_overlay"):
            self.wave_overlay.setGeometry(self.rect())
        if hasattr(self, "biofeedback_overlay"):
            self.biofeedback_overlay.setGeometry(self.rect())

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
                or self.dev_button.geometry().contains(pos)
                or self.dev_menu.geometry().contains(pos)
                or self.stats_overlay.geometry().contains(pos)
                or self.today_sessions.geometry().contains(pos)
                or self.session_details.geometry().contains(pos)
                or self.badges_view.geometry().contains(pos)
                or self.options_overlay.geometry().contains(pos)
                or self.sound_overlay.geometry().contains(pos)
                or self.breath_modes.geometry().contains(pos)
                ):
                self.menu_handler.hide_control_buttons()
                self.dev_menu.hide()
                self.stats_overlay.hide()
                self.today_sessions.hide()
                self.session_details.hide()
                self.badges_view.hide()
                self.options_overlay.hide()
                self.sound_overlay.hide()
                self.breath_modes.hide()
        return super().eventFilter(obj, event)

    def toggle_menu(self):
        self.menu_handler.toggle_menu()

    def toggle_stats(self):
        self.overlay_manager.toggle_stats()

    def close_stats(self):
        self.overlay_manager.close_stats()

    def open_today_sessions(self):
        self.overlay_manager.open_today_sessions()

    def close_today_sessions(self):
        self.overlay_manager.close_today_sessions()

    def mousePressEvent(self, event):
        pos = event.pos()
        if not (
            self.menu_button.geometry().contains(pos)
            or self.options_button.geometry().contains(pos)
            or self.stats_button.geometry().contains(pos)
            or self.end_button.geometry().contains(pos)
            or self.dev_button.geometry().contains(pos)
            or self.dev_menu.geometry().contains(pos)
            or self.stats_overlay.geometry().contains(pos)
            or self.today_sessions.geometry().contains(pos)
            or self.session_details.geometry().contains(pos)
            or self.badges_view.geometry().contains(pos)
            or self.options_overlay.geometry().contains(pos)
            or self.sound_overlay.geometry().contains(pos)
            or self.breath_modes.geometry().contains(pos)
        ):
            self.menu_handler.hide_control_buttons()
            self.dev_menu.hide()
            self.stats_overlay.hide()
            self.today_sessions.hide()
            self.session_details.hide()
            self.badges_view.hide()
            self.options_overlay.hide()
            self.sound_overlay.hide()
            self.breath_modes.hide()
        super().mousePressEvent(event)

    def on_session_complete_done(self):
        self.overlay_manager.on_session_complete_done()

    def on_session_complete_closed(self):
        self.overlay_manager.on_session_complete_closed()

    def open_session_details(self, session):
        self.overlay_manager.open_session_details(session)

    def close_session_details(self):
        self.overlay_manager.close_session_details()

    def open_today_badges(self):
        self.overlay_manager.open_today_badges()

    def open_session_badges(self, badges, return_to=None):
        self.overlay_manager.open_session_badges(badges, return_to=return_to)

    def close_badges_view(self):
        self.overlay_manager.close_badges_view()

    def load_messages(self):
        self.message_handler.load_messages()

    def build_message_schedule(self, max_count: int = 150):
        self.message_handler.build_message_schedule(max_count)

    def start_prompt_animation(self):
        self.message_handler.start_prompt_animation()

    def _update_message_font(self, value):
        self.message_handler._update_message_font(value)

    def _update_label_color(self, color):
        if isinstance(color, QColor):
            self.label.setStyleSheet(f"color:{color.name()};")
            self.current_text_color = color

    def stop_prompt_animation(self):
        self.message_handler.stop_prompt_animation()

    def display_motivational_message(self, text):
        self.message_handler.display_motivational_message(text)

    def check_motivational_message(self, count):
        self.message_handler.check_motivational_message(count)

    def toggle_options(self):
        self.menu_handler.toggle_options()

    def close_options(self):
        self.menu_handler.close_options()

    def toggle_developer_menu(self):
        self.menu_handler.toggle_developer_menu()

    def toggle_developer_speed(self):
        self.session_manager.toggle_developer_speed()

    def advance_day(self):
        self.session_manager.advance_day()

    def update_speed(self):
        self.session_manager.update_speed()

    def _setup_control_button(self, button: QPushButton) -> None:
        self.menu_handler._setup_control_button(button)

    def hide_control_buttons(self) -> None:
        self.menu_handler.hide_control_buttons()

    def show_control_buttons(self) -> None:
        self.menu_handler.show_control_buttons()

    def toggle_breath_modes(self) -> None:
        self.menu_handler.toggle_breath_modes()

    def close_breath_modes(self) -> None:
        self.menu_handler.close_breath_modes()

    def _on_pattern_selected(self, pattern: dict) -> None:
        phases = pattern.get("phases", [])
        self.circle.set_pattern(phases)
        self.current_pattern_id = pattern.get("id")
        self.menu_handler.close_breath_modes()

    # ------------------------------------------------------------------
    def _load_biofeedback_messages(self):
        path = Path(__file__).resolve().parent / "biofeedback.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            msgs = data.get("messages") if isinstance(data, dict) else data
            if isinstance(msgs, list):
                self.biofeedback_messages = msgs
        except Exception:
            self.biofeedback_messages = []

    def show_biofeedback_message(self):
        if not self.biofeedback_messages:
            self.display_session_complete()
            return
        msg = random.choice(self.biofeedback_messages).get("mensaje", "")
        self.biofeedback_overlay.raise_()
        self.biofeedback_overlay.show_message(msg)

    def display_session_complete(self):
        self.stack.setCurrentWidget(self.session_complete)
