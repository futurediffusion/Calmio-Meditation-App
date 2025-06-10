from PySide6.QtCore import Qt, Signal, QPropertyAnimation
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QGraphicsOpacityEffect


class DailyChallengePrompt(QWidget):
    """Small floating button prompting to open the daily challenge."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QPushButton("\U0001F3C6")
        self.button.setFixedSize(48, 48)
        self.button.setStyleSheet(
            "QPushButton{background-color:#4D9FFF;border:none;border-radius:24px;color:white;font-size:20px;}"
        )
        self.button.clicked.connect(self.clicked)
        layout.addWidget(self.button)

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(1.0)
        self._fade = None

    def fade_out(self):
        if self._fade and self._fade.state() != QPropertyAnimation.Stopped:
            self._fade.stop()
        self._fade = QPropertyAnimation(self.opacity, b"opacity", self)
        self._fade.setDuration(600)
        self._fade.setStartValue(self.opacity.opacity())
        self._fade.setEndValue(0)
        self._fade.finished.connect(self.hide)
        self._fade.start()
