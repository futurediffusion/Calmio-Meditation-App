from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QSequentialAnimationGroup
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect


class BioFeedbackOverlay(QWidget):
    """Simple overlay to display a biofeedback message with fade in/out."""

    done = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color:white;color:#222;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addStretch()

        self.label = QLabel("", self)
        font = QFont("Sans Serif")
        font.setPointSize(20)
        font.setWeight(QFont.Bold)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        self.opacity = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0)

        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.anim = None

    def show_message(self, text: str):
        self.label.setText(text)
        self.opacity.setOpacity(0)
        self.show()
        fade_in = QPropertyAnimation(self.opacity, b"opacity", self)
        fade_in.setDuration(1000)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_out = QPropertyAnimation(self.opacity, b"opacity", self)
        fade_out.setDuration(2000)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        group = QSequentialAnimationGroup(self)
        group.addAnimation(fade_in)
        group.addPause(1500)
        group.addAnimation(fade_out)
        group.finished.connect(self._on_done)
        group.start()
        self.anim = group

    def _on_done(self):
        self.hide()
        self.done.emit()
