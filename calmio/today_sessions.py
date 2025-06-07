from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QGraphicsDropShadowEffect,
)


class TodaySessionsView(QWidget):
    """Display list of today's sessions."""

    back_requested = Signal()
    session_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color:#FAFAFA;color:#444;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header = QHBoxLayout()
        self.back_btn = QPushButton("\u2190")
        self.back_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;}"
        )
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        title = QLabel("Sesiones de hoy")
        title_font = QFont("Sans Serif")
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Medium)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title, alignment=Qt.AlignCenter)
        header.addStretch()
        layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setSpacing(10)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.container)

    def set_sessions(self, sessions):
        # clear old widgets except stretch
        for i in reversed(range(self.list_layout.count() - 1)):
            item = self.list_layout.takeAt(i)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        for idx, s in enumerate(sessions):
            card = QFrame()
            card.setStyleSheet("background:#E0F0FF;border-radius:15px;padding:6px;")
            eff = QGraphicsDropShadowEffect(self)
            eff.setBlurRadius(8)
            eff.setOffset(0, 2)
            card.setGraphicsEffect(eff)
            card.setCursor(Qt.PointingHandCursor)

            row = QHBoxLayout(card)
            row.setContentsMargins(6, 2, 6, 2)
            text = self._format_session_text(s)
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignLeft)
            lbl.setWordWrap(True)
            row.addWidget(lbl)
            row.addStretch()
            if idx == 0:
                clock = QLabel("\u23F0")
                clock.setStyleSheet("color:#777;")
                row.addWidget(clock)
            self.list_layout.insertWidget(idx, card)

            def handler(evt, sess=s):
                self.session_selected.emit(sess)
            card.mouseReleaseEvent = handler

    def _format_session_text(self, s):
        start = s.get("start", "").split(" ")[-1]
        duration = s.get("duration", 0)
        breaths = s.get("breaths", 0)
        inhale = s.get("last_inhale", 0.0)
        exhale = s.get("last_exhale", 0.0)
        cycles = s.get("cycles", [])
        first_cycle = cycles[0] if cycles and isinstance(cycles[0], dict) else None
        last_cycle = cycles[-1] if cycles and isinstance(cycles[-1], dict) else None
        if first_cycle:
            first_dur = first_cycle.get("inhale", 0) + first_cycle.get("exhale", 0)
        else:
            first_dur = inhale + exhale
        if last_cycle:
            last_dur = last_cycle.get("inhale", 0) + last_cycle.get("exhale", 0)
        else:
            last_dur = inhale + exhale
        if duration < 60:
            dur_str = f"{duration:.0f}s"
        else:
            m = int(duration // 60)
            s_rem = int(duration % 60)
            dur_str = f"{m}m" + (f" {s_rem}s" if s_rem else "")
        return (
            f"\u23F0 {start} \u2022 \u23F1 {dur_str} "
            f"\u2022 \U0001FAC1 {breaths} "
            f"\u2022 \u2B06\uFE0F {first_dur:.2f}s \u2B07\uFE0F {last_dur:.2f}s"
        )

