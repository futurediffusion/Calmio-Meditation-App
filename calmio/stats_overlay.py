from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect,
)

from .progress_circle import ProgressCircle


class StatsOverlay(QWidget):
    view_sessions = Signal()
    session_requested = Signal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color:#FAFAFA; border-radius:20px; color:#444;"
        )
        self._last_session_data = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("\u2190")
        self.back_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;}"
        )
        header_layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        title = QLabel("Today's Meditation", self)
        title_font = QFont("Sans Serif")
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Medium)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title, alignment=Qt.AlignCenter)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        self.back_btn.clicked.connect(self.on_back)

        self.progress = ProgressCircle(self)

        self.streak_label = QLabel("\ud83d\udd25 1 d\u00eda consecutivo", self)
        streak_font = QFont("Sans Serif")
        streak_font.setPointSize(12)
        self.streak_label.setFont(streak_font)
        streak_card = QFrame()
        streak_card.setStyleSheet(
            "background:white;border-radius:15px;"
            "padding:10px;"
        )
        streak_shadow = QGraphicsDropShadowEffect(self)
        streak_shadow.setBlurRadius(8)
        streak_shadow.setOffset(0, 2)
        streak_card.setGraphicsEffect(streak_shadow)
        streak_layout = QHBoxLayout(streak_card)
        streak_layout.addWidget(self.streak_label, alignment=Qt.AlignCenter)

        self.sessions_btn = QPushButton("View Sessions")
        self.sessions_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#CCE4FF;border:none;border-radius:20px;"
            "padding:12px 24px;font-size:14px;}"
        )

        self.sessions_btn.clicked.connect(self.view_sessions.emit)

        self.last_session = QFrame()
        self.last_session.setStyleSheet(
            "background:#E0F0FF;border-radius:15px;padding:6px;"
        )
        ls_shadow = QGraphicsDropShadowEffect(self)
        ls_shadow.setBlurRadius(8)
        ls_shadow.setOffset(0, 2)
        self.last_session.setGraphicsEffect(ls_shadow)
        ls_layout = QHBoxLayout(self.last_session)
        ls_layout.setContentsMargins(6, 2, 6, 2)
        self.ls_text = QLabel("")
        self.ls_text.setAlignment(Qt.AlignLeft)
        self.ls_text.setWordWrap(True)
        ls_tag = QLabel("Last session")
        ls_tag.setStyleSheet(
            "background:#eee;border-radius:10px;padding:2px 6px;"
            "font-size:10px;color:#777;"
        )
        ls_layout.addWidget(self.ls_text)
        ls_layout.addStretch()
        ls_layout.addWidget(ls_tag)
        self.last_session.setCursor(Qt.PointingHandCursor)
        self.last_session.mouseReleaseEvent = self._on_last_session_clicked

        nav_layout = QHBoxLayout()
        self.today_btn = QPushButton("Today")
        self.week_btn = QPushButton("Week")
        self.month_btn = QPushButton("Month")
        btn_style = (
            "QPushButton{background:white;border-radius:15px;"
            "padding:8px 16px;color:#777;}"
        )
        for btn in (self.today_btn, self.week_btn, self.month_btn):
            btn.setStyleSheet(btn_style)
        self.today_btn.setStyleSheet(
            "QPushButton{background:#CCE4FF;border-radius:15px;"
            "padding:8px 16px;color:#444;}"
        )
        nav_layout.addWidget(self.today_btn)
        nav_layout.addWidget(self.week_btn)
        nav_layout.addWidget(self.month_btn)

        layout.addWidget(self.progress, alignment=Qt.AlignCenter)
        layout.addWidget(streak_card, alignment=Qt.AlignCenter)
        layout.addWidget(self.sessions_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.last_session)
        layout.addStretch()
        layout.addLayout(nav_layout)

    def update_streak(self, days):
        if days == 1:
            text = "\ud83d\udd25 1 d\u00eda consecutivo"
        else:
            text = f"\ud83d\udd25 {days} d\u00edas consecutivos"
        self.streak_label.setText(text)

    def update_minutes(self, seconds):
        self.progress.set_seconds(seconds)

    def update_last_session(self, start, duration, breaths, inhale, exhale, cycles=None):
        self._last_session_data = {
            "start": start,
            "duration": duration,
            "breaths": breaths,
            "last_inhale": inhale,
            "last_exhale": exhale,
            "cycles": cycles or [],
        }
        if duration < 60:
            dur_str = f"{duration:.0f}s"
        else:
            m = int(duration // 60)
            s = int(duration % 60)
            dur_str = f"{m}m" + (f" {s}s" if s else "")
        self.ls_text.setText(
            f"\u23F0 {start} \u2022 \u23F1 {dur_str} \u2022 \U0001FAC1 {breaths} \u2022 \u2B06\uFE0F {inhale:.2f}s \u2B07\uFE0F {exhale:.2f}s"
        )

    def on_back(self):
        parent = self.parent()
        if hasattr(parent, "close_stats"):
            parent.close_stats()
        else:
            self.hide()

    def _on_last_session_clicked(self, event):
        if self._last_session_data:
            self.session_requested.emit(self._last_session_data)
