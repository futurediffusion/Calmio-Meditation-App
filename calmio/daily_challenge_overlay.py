from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton


class DailyChallengeOverlay(QWidget):
    """Overlay to display and complete the daily challenge."""

    completed = Signal()
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color:#FAFAFA;color:#444;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header = QHBoxLayout()
        self.title = QLabel("Reto del d\u00eda")
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Medium)
        self.title.setFont(t_font)
        self.title.setAlignment(Qt.AlignCenter)
        header.addStretch()
        header.addWidget(self.title, alignment=Qt.AlignCenter)

        self.close_btn = QPushButton("\u2715")
        self.close_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;color:#888;}"
        )
        self.close_btn.clicked.connect(self._close)
        header.addWidget(self.close_btn, alignment=Qt.AlignRight)
        layout.addLayout(header)

        self.challenge_lbl = QLabel("")
        font = QFont("Sans Serif")
        font.setPointSize(14)
        self.challenge_lbl.setFont(font)
        self.challenge_lbl.setWordWrap(True)
        self.challenge_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.challenge_lbl, alignment=Qt.AlignCenter)

        self.complete_btn = QPushButton("Marcar como logrado")
        self.complete_btn.setStyleSheet(
            "QPushButton{"
            "background-color:#4D9FFF;border:none;border-radius:20px;"
            "padding:12px 24px;color:white;font-size:14px;}"
        )
        self.complete_btn.clicked.connect(self._on_complete)
        layout.addWidget(self.complete_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

    def set_challenge(self, text: str, completed: bool = False) -> None:
        self.challenge_lbl.setText(text)
        if completed:
            self.complete_btn.setText("\u2714 Hecho")
            self.complete_btn.setEnabled(False)
        else:
            self.complete_btn.setText("Marcar como logrado")
            self.complete_btn.setEnabled(True)

    def _on_complete(self):
        self.complete_btn.setText("\u2714 Hecho")
        self.complete_btn.setEnabled(False)
        self.completed.emit()

    def _close(self):
        self.hide()
        self.closed.emit()
