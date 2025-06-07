from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
    QPushButton,
)

from .progress_circle import ProgressCircle


class StatsOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color:#FAFAFA; border-radius:20px; color:#444;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Today's Meditation", self)
        title_font = QFont("Sans Serif")
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Medium)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)

        self.progress = ProgressCircle(self)

        self.streak_label = QLabel("\ud83d\udd25 3 days in a row", self)
        streak_font = QFont("Sans Serif")
        streak_font.setPointSize(12)
        self.streak_label.setFont(streak_font)
        streak_card = QFrame()
        streak_card.setStyleSheet(
            "background:white;border-radius:15px;"
            "padding:10px;"
            "box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
        )
        streak_layout = QHBoxLayout(streak_card)
        streak_layout.addWidget(self.streak_label, alignment=Qt.AlignCenter)

        self.sessions_btn = QPushButton("View Sessions")
        self.sessions_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#CCE4FF;border:none;border-radius:20px;"
            "padding:12px 24px;font-size:14px;}"
        )

        self.last_session = QFrame()
        self.last_session.setStyleSheet(
            "background:white;border-radius:15px;padding:10px;"
            "box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
        )
        ls_layout = QHBoxLayout(self.last_session)
        ls_text = QLabel("08:00 \u2022 10min \u2022 83 br \u2022 5s last")
        ls_tag = QLabel("Last session")
        ls_tag.setStyleSheet(
            "background:#eee;border-radius:10px;padding:2px 6px;"
            "font-size:10px;color:#777;"
        )
        ls_layout.addWidget(ls_text)
        ls_layout.addStretch()
        ls_layout.addWidget(ls_tag)

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

        layout.addWidget(title)
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)
        layout.addWidget(streak_card, alignment=Qt.AlignCenter)
        layout.addWidget(self.sessions_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.last_session)
        layout.addStretch()
        layout.addLayout(nav_layout)

    def update_minutes(self, m):
        self.progress.set_minutes(m)
