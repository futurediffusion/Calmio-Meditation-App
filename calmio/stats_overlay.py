from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect,
    QStackedWidget,
)

from .progress_circle import ProgressCircle
from .weekly_stats import WeeklyStatsView
from .monthly_stats import MonthlyStatsView


class StatsOverlay(QWidget):
    view_sessions = Signal()
    session_requested = Signal(dict)
    view_badges_today = Signal()
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

        self.title = QLabel("Meditaci\u00f3n de hoy", self)
        title_font = QFont("Sans Serif")
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Medium)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title, alignment=Qt.AlignCenter)
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

        self.sessions_btn = QPushButton("Ver sesiones")
        self.sessions_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#CCE4FF;border:none;border-radius:20px;"
            "padding:12px 24px;font-size:14px;}"
        )

        self.sessions_btn.clicked.connect(self.view_sessions.emit)

        self.badges_btn = QPushButton("Logros alcanzados hoy")
        self.badges_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#CCE4FF;border:none;border-radius:20px;"
            "padding:12px 24px;font-size:14px;}"
        )
        self.badges_btn.clicked.connect(self.view_badges_today.emit)

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
        ls_tag = QLabel("\u00daltima sesi\u00f3n")
        ls_tag.setStyleSheet(
            "background:#eee;border-radius:10px;padding:2px 6px;"
            "font-size:10px;color:#777;"
        )
        ls_layout.addWidget(self.ls_text)
        ls_layout.addStretch()
        ls_layout.addWidget(ls_tag)
        self.last_session.setCursor(Qt.PointingHandCursor)
        self.last_session.mouseReleaseEvent = self._on_last_session_clicked

        # Today view container
        self.today_container = QWidget()
        today_layout = QVBoxLayout(self.today_container)
        today_layout.setSpacing(10)
        today_layout.addWidget(self.progress, alignment=Qt.AlignCenter)
        today_layout.addWidget(streak_card, alignment=Qt.AlignCenter)
        today_layout.addWidget(self.sessions_btn, alignment=Qt.AlignCenter)
        today_layout.addWidget(self.badges_btn, alignment=Qt.AlignCenter)
        today_layout.addWidget(self.last_session)
        today_layout.addStretch()

        self.week_view = WeeklyStatsView(self)
        self.month_view = MonthlyStatsView(self)

        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.today_container)
        self.content_stack.addWidget(self.week_view)
        self.content_stack.addWidget(self.month_view)

        nav_layout = QHBoxLayout()
        self.today_btn = QPushButton("Hoy")
        self.week_btn = QPushButton("Semana")
        self.month_btn = QPushButton("Mes")
        btn_style = (
            "QPushButton{background:white;border-radius:15px;"
            "padding:8px 16px;color:#777;}"
        )
        for btn in (self.today_btn, self.week_btn, self.month_btn):
            btn.setStyleSheet(btn_style)
        self.today_btn.setStyleSheet(
            "QPushButton{background:#CCE4FF;border-radius:15px;"
            "padding:8px 16px;color:#444;font-weight:bold;}"
        )
        nav_layout.addWidget(self.today_btn)
        nav_layout.addWidget(self.week_btn)
        nav_layout.addWidget(self.month_btn)

        layout.addWidget(self.content_stack)
        layout.addLayout(nav_layout)

        self.today_btn.clicked.connect(lambda: self.show_tab(0))
        self.week_btn.clicked.connect(lambda: self.show_tab(1))
        self.month_btn.clicked.connect(lambda: self.show_tab(2))

        self.show_tab(0)

    def update_streak(self, days):
        if days == 1:
            text = "\ud83d\udd25 1 d\u00eda consecutivo"
        else:
            text = f"\ud83d\udd25 {days} d\u00edas consecutivos"
        self.streak_label.setText(text)

    def update_minutes(self, seconds):
        self.progress.set_seconds(seconds)

    def update_badges(self, badges):
        if isinstance(badges, dict):
            count = sum(badges.values())
        else:
            count = len(badges)
        self.badges_btn.setText(f"Logros de hoy ({count})")
        self.badges_btn.setEnabled(count > 0)

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
        first_cycle = (cycles[0] if cycles and isinstance(cycles[0], dict) else None)
        last_cycle = (cycles[-1] if cycles and isinstance(cycles[-1], dict) else None)
        if first_cycle:
            first_dur = first_cycle.get("inhale", 0) + first_cycle.get("exhale", 0)
        else:
            first_dur = inhale + exhale
        if last_cycle:
            last_dur = last_cycle.get("inhale", 0) + last_cycle.get("exhale", 0)
        else:
            last_dur = inhale + exhale
        self.ls_text.setText(
            f"\u23F0 {start} \u2022 \u23F1 {dur_str} \u2022 \U0001FAC1 {breaths} \u2022 \u2B06\uFE0F {first_dur:.2f}s \u2B07\uFE0F {last_dur:.2f}s"
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

    def show_tab(self, index: int):
        self.content_stack.setCurrentIndex(index)
        btns = [self.today_btn, self.week_btn, self.month_btn]
        for i, b in enumerate(btns):
            if i == index:
                b.setStyleSheet(
                    "QPushButton{background:#CCE4FF;border-radius:15px;"
                    "padding:8px 16px;color:#444;font-weight:bold;}"
                )
            else:
                b.setStyleSheet(
                    "QPushButton{background:white;border-radius:15px;"
                    "padding:8px 16px;color:#777;}"
                )
        if index == 1:
            self.refresh_week()
        if index == 2:
            self.refresh_month()
        if index == 0:
            self.title.setText("Meditaci\u00f3n de hoy")
        elif index == 1:
            self.title.setText("Estad\u00edsticas semanales")
        else:
            self.title.setText("Estad\u00edsticas mensuales")

    def refresh_week(self):
        store = getattr(self.parent(), "data_store", None)
        if not store:
            return
        data = store.get_weekly_summary()
        self.week_view.set_stats(
            data["minutes_per_day"],
            data["total"],
            data["average"],
            data["longest_day"],
            data.get("longest_time", ""),
            data["longest_minutes"],
        )

    def refresh_month(self):
        store = getattr(self.parent(), "data_store", None)
        if not store:
            return
        dt = datetime.now()
        data = store.get_monthly_summary(dt.year, dt.month)
        self.month_view.set_stats(
            data["minutes_per_week"],
            data["total"],
            data["average"],
            data["best_week"],
            data["longest_streak"],
            data.get("goal", 600),
        )
