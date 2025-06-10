from PySide6.QtCore import Qt, Signal, QPropertyAnimation
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)


class SessionComplete(QWidget):
    done = Signal()
    closed = Signal()
    badges_requested = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color:#FAFAFA;color:#444;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        title = QLabel("Sesi\u00f3n completada")
        title_font = QFont("Sans Serif")
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Medium)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addStretch()
        header_layout.addWidget(title, alignment=Qt.AlignCenter)

        self.close_btn = QPushButton("\u2715")
        self.close_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;color:#888;}"
        )
        self.close_btn.clicked.connect(self.closed.emit)
        header_layout.addWidget(self.close_btn, alignment=Qt.AlignRight)
        layout.addLayout(header_layout)

        card = QFrame()
        card.setStyleSheet(
            "background:rgba(255,255,255,0.8);border-radius:15px;padding:15px;"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        def row(text):
            lbl = QLabel(text)
            row_layout = QHBoxLayout()
            row_layout.addWidget(lbl)
            row_widget = QWidget()
            row_widget.setLayout(row_layout)
            return row_widget, lbl

        self.duration_row, self.duration_lbl = row("\u23F1 Duraci\u00f3n: 0s")
        self.breaths_row, self.breaths_lbl = row("\U0001FAC1 Respiraciones: 0")
        self.inhale_row, self.inhale_lbl = row("\u2B06\ufe0f Inhalar: 0.00s")
        self.exhale_row, self.exhale_lbl = row("\u2B07\ufe0f Exhalar: 0.00s")
        self.start_row, self.start_lbl = row("\u23F0 Inicio: --")
        self.end_row, self.end_lbl = row("\u23F0 Fin: --")

        for rw in (
            self.duration_row,
            self.breaths_row,
            self.inhale_row,
            self.exhale_row,
            self.start_row,
            self.end_row,
        ):
            card_layout.addWidget(rw)

        layout.addWidget(card)

        self.badge_btn = QPushButton("")
        self.badge_btn.setCursor(Qt.PointingHandCursor)
        self.badge_btn.setStyleSheet(
            "QPushButton{background:none;border:none;color:#F39C12;font-weight:bold;}"
        )
        badge_font = QFont("Sans Serif")
        badge_font.setPointSize(14)
        badge_font.setWeight(QFont.Bold)
        self.badge_btn.setFont(badge_font)
        self.badge_btn.clicked.connect(self._emit_badges)
        self.badge_btn.hide()
        layout.addWidget(self.badge_btn)
        self._badges = []

        self.phrase = QLabel("Lleva esta calma contigo durante el d\u00eda.")
        ph_font = QFont("Sans Serif")
        ph_font.setPointSize(12)
        self.phrase.setFont(ph_font)
        self.phrase.setAlignment(Qt.AlignCenter)
        self.phrase.setStyleSheet("color:#666;")
        layout.addWidget(self.phrase)

        # ephemeral star animation widgets
        self._stars = []
        for _ in range(15):
            lbl = QLabel("\u2728", self)
            lbl.setStyleSheet("font-size:24px;color:#F5B041;")
            lbl.hide()
            self._stars.append(lbl)

        self.done_btn = QPushButton("Listo")
        self.done_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#4D9FFF;border:none;border-radius:20px;"
            "padding:12px 24px;color:white;font-size:16px;}"
        )
        self.done_btn.clicked.connect(self.done.emit)
        layout.addWidget(self.done_btn, alignment=Qt.AlignCenter)

    def set_stats(self, duration, breaths, inhale, exhale, start, end):
        if duration < 60:
            self.duration_lbl.setText(f"\u23F1 Duraci\u00f3n: {duration:.0f}s")
        else:
            m = int(duration // 60)
            s = int(duration % 60)
            dur_str = f"{m}m" + (f" {s}s" if s else "")
            self.duration_lbl.setText(f"\u23F1 Duraci\u00f3n: {dur_str}")
        self.breaths_lbl.setText(f"\U0001FAC1 Respiraciones: {breaths}")
        self.inhale_lbl.setText(f"\u2B06\ufe0f Inhalar: {inhale:.2f}s")
        self.exhale_lbl.setText(f"\u2B07\ufe0f Exhalar: {exhale:.2f}s")
        self.start_lbl.setText(f"\u23F0 Inicio: {start}")
        self.end_lbl.setText(f"\u23F0 Fin: {end}")

    def show_badges(self, badges):
        from .achievements import get_badge_info
        self._badges = list(badges)
        if badges:
            info = get_badge_info(badges[-1])
            name = info.get("nombre", badges[-1])
            self.badge_btn.setText("\u2728 " + name)
            self.badge_btn.show()
        else:
            self.badge_btn.hide()
        self.play_completion_animation()

    def play_completion_animation(self):
        """Show ephemeral twinkling stars when the session is complete."""
        import random

        # Clean up previous effects and hide stars
        for star in self._stars:
            if star.graphicsEffect():
                star.graphicsEffect().deleteLater()
                star.setGraphicsEffect(None)
            star.hide()

        for star in self._stars:
            x = random.randint(0, max(0, self.width() - star.width()))
            y = random.randint(0, max(0, self.height() - star.height()))
            star.move(x, y)
            effect = QGraphicsOpacityEffect(star)
            star.setGraphicsEffect(effect)
            effect.setOpacity(1)
            star.show()

            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(1000)
            anim.setStartValue(1)
            anim.setEndValue(0)
            anim.finished.connect(lambda _=None, s=star: self._hide_star(s))
            anim.start()

    def _hide_star(self, star):
        """Hide *star* and remove its graphics effect once animation finishes."""
        star.hide()
        eff = star.graphicsEffect()
        if eff:
            eff.deleteLater()
            star.setGraphicsEffect(None)

    def _emit_badges(self, evt=None):
        if self._badges:
            self.badges_requested.emit(self._badges)

