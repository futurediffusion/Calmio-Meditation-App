from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
)


class SessionComplete(QWidget):
    done = Signal()
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color:#FAFAFA;color:#444;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        title = QLabel("Session Complete")
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

        self.duration_row, self.duration_lbl = row("\u23F1 Duration: 0 min")
        self.breaths_row, self.breaths_lbl = row("\u1F4A8 Breaths: 0")
        self.longest_row, self.longest_lbl = row("\u23F2 Longest breath: 0s")
        self.start_row, self.start_lbl = row("\u23F0 Start time: --")
        self.end_row, self.end_lbl = row("\u23F0 End time: --")

        for rw in (
            self.duration_row,
            self.breaths_row,
            self.longest_row,
            self.start_row,
            self.end_row,
        ):
            card_layout.addWidget(rw)

        layout.addWidget(card)

        self.phrase = QLabel("Take this calm with you into the day.")
        ph_font = QFont("Sans Serif")
        ph_font.setPointSize(12)
        self.phrase.setFont(ph_font)
        self.phrase.setAlignment(Qt.AlignCenter)
        self.phrase.setStyleSheet("color:#666;")
        layout.addWidget(self.phrase)

        self.done_btn = QPushButton("Done")
        self.done_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#4D9FFF;border:none;border-radius:20px;"
            "padding:12px 24px;color:white;font-size:16px;}"
        )
        self.done_btn.clicked.connect(self.done.emit)
        layout.addWidget(self.done_btn, alignment=Qt.AlignCenter)

    def set_stats(self, duration, breaths, longest, start, end):
        self.duration_lbl.setText(f"\u23F1 Duration: {duration} min")
        self.breaths_lbl.setText(f"\U0001F4A8 Breaths: {breaths}")
        self.longest_lbl.setText(f"\u23F2 Longest breath: {longest}s")
        self.start_lbl.setText(f"\u23F0 Start time: {start}")
        self.end_lbl.setText(f"\u23F0 End time: {end}")

