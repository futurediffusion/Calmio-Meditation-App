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
)
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

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{border:none;}")
        layout.addWidget(self.scroll)

        container = QWidget()
        self.scroll.setWidget(container)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(15)

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
        c_layout.addLayout(self.pattern_container)
        c_layout.addStretch()

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
        row = QFrame()
        row.setStyleSheet(
            "background:white;border-radius:15px;padding:10px;"
        )
        row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        r_layout = QHBoxLayout(row)
        r_layout.setSpacing(8)
        name_lbl = QLabel(pat.get("name", ""))
        name_font = QFont("Sans Serif")
        name_font.setPointSize(14)
        name_lbl.setFont(name_font)
        name_lbl.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        desc = pat.get("description", "")
        count_str = " / ".join(str(p.get("duration", 0)) for p in pat.get("phases", []))
        info_lbl = QLabel(f"{count_str}s – {desc}")
        info_lbl.setWordWrap(True)
        info_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sel_btn = QPushButton("Usar")
        sel_btn.setStyleSheet(
            "QPushButton{background-color:#CCE4FF;border:none;border-radius:10px;padding:6px 12px;}"
        )
        sel_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sel_btn.clicked.connect(lambda _, p=pat: self.pattern_selected.emit(p))
        r_layout.addWidget(name_lbl)
        r_layout.addStretch(1)
        r_layout.addWidget(info_lbl, stretch=2)
        r_layout.addWidget(sel_btn)
        self.pattern_container.addWidget(row)


