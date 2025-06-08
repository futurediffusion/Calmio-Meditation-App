from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QFrame,
    QGraphicsDropShadowEffect,
)


class BadgesView(QWidget):
    """Simple list view for badges."""

    back_requested = Signal()

    def __init__(self, parent=None, title="Logros"):
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
        header.addWidget(self.back_btn)
        header.addStretch()

        self.title_lbl = QLabel(title)
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Bold)
        self.title_lbl.setFont(t_font)
        self.title_lbl.setAlignment(Qt.AlignCenter)
        header.addWidget(self.title_lbl, alignment=Qt.AlignCenter)
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

    LEVEL_EMOJIS = [
        "\ud83e\udd49",
        "\ud83e\udd49",
        "\ud83e\udd49",
        "\ud83e\udd48",
        "\ud83e\udd48",
        "\ud83e\udd47",
        "\ud83e\udd47",
        "\ud83d\udc8e",
        "\ud83d\udc8e",
        "\ud83c\udfc6",
    ]

    LEVEL_COLORS = [
        "#E0F0FF",
        "#D0E8FF",
        "#C0E0FF",
        "#B0D8FF",
        "#A0D0FF",
        "#90C8FF",
        "#80C0FF",
        "#70B8FF",
        "#60B0FF",
        "#50A8FF",
    ]

    def set_badges(self, badges):
        from .badges import BADGE_NAMES

        for i in reversed(range(self.list_layout.count() - 1)):
            item = self.list_layout.takeAt(i)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if isinstance(badges, dict):
            items = badges.items()
        else:
            from collections import Counter
            items = Counter(badges).items()

        for idx, (code, count) in enumerate(items):
            card = QFrame()
            level = max(1, min(count, len(self.LEVEL_COLORS)))
            color = self.LEVEL_COLORS[level - 1]
            card.setStyleSheet(
                f"background:{color};border-radius:15px;padding:6px;"
            )
            eff = QGraphicsDropShadowEffect(self)
            eff.setBlurRadius(8)
            eff.setOffset(0, 2)
            card.setGraphicsEffect(eff)
            row = QHBoxLayout(card)
            row.setContentsMargins(6, 2, 6, 2)
            level = min(count, len(self.LEVEL_EMOJIS))
            medal = self.LEVEL_EMOJIS[level - 1]
            text = QLabel(f"{BADGE_NAMES.get(code, code)} - Nivel {level}")
            txt_font = QFont("Sans Serif")
            txt_font.setBold(True)
            text.setFont(txt_font)
            text.setAlignment(Qt.AlignLeft)
            text.setWordWrap(True)
            row.addWidget(text)
            row.addStretch()
            medal_lbl = QLabel(medal)
            medal_lbl.setAlignment(Qt.AlignRight)
            row.addWidget(medal_lbl)
            self.list_layout.insertWidget(idx, card)

