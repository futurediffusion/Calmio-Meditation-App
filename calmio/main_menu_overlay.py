from PySide6.QtCore import Qt, Signal, QPropertyAnimation
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QFont


class MainMenuOverlay(QWidget):
    """Central modal menu with glassmorphism style."""

    music_requested = Signal()
    breathing_requested = Signal()
    mantras_requested = Signal()
    achievements_requested = Signal()
    settings_requested = Signal()
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 180);"
            "border-radius:24px;"
            "color:#222;"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0)

        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.music_btn = self._create_btn("\U0001F3B5", "M\u00fasica")
        self.breath_btn = self._create_btn("\U0001FAC1", "Respiraci\u00f3n")
        self.mantras_btn = self._create_btn("\u2764\ufe0f", "Mantras")
        self.ach_btn = self._create_btn("\U0001F9E0", "Logros")
        self.settings_btn = self._create_btn("\u2699\ufe0f", "Ajustes")
        self.close_btn = self._create_btn("\U0001F534", "Cerrar")

        layout.addWidget(self.music_btn, 0, 0)
        layout.addWidget(self.breath_btn, 0, 1)
        layout.addWidget(self.mantras_btn, 1, 0)
        layout.addWidget(self.ach_btn, 1, 1)
        layout.addWidget(self.settings_btn, 2, 0)
        layout.addWidget(self.close_btn, 2, 1)

        self.music_btn.clicked.connect(self.music_requested.emit)
        self.breath_btn.clicked.connect(self.breathing_requested.emit)
        self.mantras_btn.clicked.connect(self.mantras_requested.emit)
        self.ach_btn.clicked.connect(self.achievements_requested.emit)
        self.settings_btn.clicked.connect(self.settings_requested.emit)
        self.close_btn.clicked.connect(self.close)

        self.anim = None

    def _create_btn(self, icon: str, text: str) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton{"
            "background: rgba(255,255,255,200);"
            "border:none;border-radius:20px;"
            "padding:10px;"
            "}"
            "QPushButton:hover{background: rgba(255,255,255,230);}"
        )
        vbox = QVBoxLayout(btn)
        vbox.setContentsMargins(5, 5, 5, 5)
        icon_lbl = QLabel(icon)
        icon_font = QFont("Sans Serif")
        icon_font.setPointSize(24)
        icon_lbl.setFont(icon_font)
        icon_lbl.setAlignment(Qt.AlignCenter)
        text_lbl = QLabel(text)
        text_font = QFont("Sans Serif")
        text_font.setPointSize(16)
        text_lbl.setFont(text_font)
        text_lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(icon_lbl)
        vbox.addWidget(text_lbl)
        return btn

    def open(self):
        parent = self.parent() or self
        w = int(parent.width() * 0.8)
        h = int(parent.height() * 0.6)
        x = (parent.width() - w) // 2
        y = (parent.height() - h) // 2
        self.setGeometry(x, y, w, h)
        self.show()
        self.raise_()
        self._animate(True)

    def close(self):
        self._animate(False)

    def _animate(self, opening: bool):
        if self.anim:
            self.anim.stop()
        anim = QPropertyAnimation(self.opacity, b"opacity", self)
        anim.setDuration(250)
        if opening:
            anim.setStartValue(0)
            anim.setEndValue(1)
        else:
            anim.setStartValue(self.opacity.opacity())
            anim.setEndValue(0)
            anim.finished.connect(super().hide)
            anim.finished.connect(self.closed.emit)
        anim.start()
        self.anim = anim
