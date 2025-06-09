from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QLayout,
    QGraphicsDropShadowEffect,
)
from .font_utils import get_emoji_font
import json
from pathlib import Path


class BreathModesOverlay(QWidget):
    """Overlay listing scientific breathing patterns."""

    back_requested = Signal()
    pattern_selected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color:#FAFAFA;border-radius:20px;color:#444;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetMinimumSize)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{border:none;}")
        self.scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.scroll)

        container = QWidget()
        self.scroll.setWidget(container)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(15)
        c_layout.setSizeConstraint(QLayout.SetMinimumSize)

        header = QHBoxLayout()
        self.back_btn = QPushButton("\u2190")
        self.back_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;}"
        )
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        title = QLabel("Modos de respiración")
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Medium)
        title.setFont(t_font)
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title, alignment=Qt.AlignCenter)
        header.addStretch()
        c_layout.addLayout(header)

        self.pattern_container = QVBoxLayout()
        self.pattern_container.setSpacing(10)
        self.pattern_container.setSizeConstraint(QLayout.SetMinimumSize)
        c_layout.addLayout(self.pattern_container)
        c_layout.addStretch()

        self.cards = []
        self.name_labels = []
        self.desc_labels = []
        self._load_patterns()

    def _load_patterns(self):
        patterns_file = Path(__file__).with_name("breath_patterns.json")
        try:
            data = json.loads(patterns_file.read_text(encoding="utf-8"))
        except Exception:
            data = []
        for pat in data:
            self._add_pattern_row(pat)

    def _add_pattern_row(self, pat: dict) -> None:
        card = QFrame()
        card.setObjectName("patternCard")
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(
            "QFrame#patternCard{background:white;border-radius:15px;}"
            "QFrame#patternCard:hover{background:#F2F2F2;}"
        )
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(8)
        eff.setOffset(0, 2)
        card.setGraphicsEffect(eff)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        icon_lbl = QLabel(pat.get("icon", ""))
        icon_lbl.setFont(get_emoji_font(18))
        icon_lbl.setAlignment(Qt.AlignCenter)

        text_col = QVBoxLayout()
        name_lbl = QLabel(pat.get("name", ""))
        name_font = QFont("Sans Serif")
        name_font.setPointSize(14)
        name_font.setWeight(QFont.Bold)
        name_lbl.setFont(name_font)
        desc_lbl = QLabel(pat.get("description", ""))
        desc_lbl.setWordWrap(True)
        desc_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        text_col.addWidget(name_lbl)
        text_col.addWidget(desc_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_col)

        card.mouseReleaseEvent = lambda e, p=pat: self.pattern_selected.emit(p)

        self.pattern_container.addWidget(card)
        self.cards.append(card)
        self.name_labels.append(name_lbl)
        self.desc_labels.append(desc_lbl)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        max_w = int(self.width() * 0.9)
        font_size = 12 if self.width() < 400 else 14
        for card in self.cards:
            card.setMaximumWidth(max_w)
        for lbl in self.name_labels + self.desc_labels:
            f = lbl.font()
            f.setPointSize(font_size)
            lbl.setFont(f)



