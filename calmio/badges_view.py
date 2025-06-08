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
        header.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        self.title_lbl = QLabel(title)
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Medium)
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

    def set_badges(self, badges):
        from .badges import BADGE_NAMES

        for i in reversed(range(self.list_layout.count() - 1)):
            item = self.list_layout.takeAt(i)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        for idx, b in enumerate(badges):
            card = QFrame()
            card.setStyleSheet("background:#E0F0FF;border-radius:15px;padding:6px;")
            eff = QGraphicsDropShadowEffect(self)
            eff.setBlurRadius(8)
            eff.setOffset(0, 2)
            card.setGraphicsEffect(eff)
            row = QHBoxLayout(card)
            row.setContentsMargins(6, 2, 6, 2)
            label = QLabel(BADGE_NAMES.get(b, b))
            label.setAlignment(Qt.AlignLeft)
            label.setWordWrap(True)
            row.addWidget(label)
            self.list_layout.insertWidget(idx, card)

