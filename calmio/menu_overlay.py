from PySide6.QtCore import Qt, Signal, QPropertyAnimation
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGridLayout,
    QGraphicsOpacityEffect,
)
from .font_utils import get_emoji_font


class MenuOverlay(QWidget):
    """Floating modal menu with glass style."""

    breath_modes_requested = Signal()
    sound_requested = Signal()
    stats_requested = Signal()
    end_requested = Signal()
    achievements_requested = Signal()
    settings_requested = Signal()
    developer_requested = Signal()
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background:rgba(255,255,255,0.95);border-radius:24px;color:#444;"
        )

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self.back_btn = QPushButton("\u2190")
        self.back_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;}"
        )
        self.back_btn.clicked.connect(self.hide_with_anim)
        header.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        header.addStretch()
        layout.addLayout(header)

        self.grid = QGridLayout()
        self.grid.setSpacing(15)
        layout.addLayout(self.grid)
        layout.addStretch()

        self.buttons = []
        self._add_button(0, 0, "\U0001FAC1", "Respiraciones", self.breath_modes_requested)
        self._add_button(0, 1, "\U0001F3B5", "Sonido", self.sound_requested)
        self._add_button(1, 0, "\U0001F4CA", "Estad\u00edsticas", self.stats_requested)
        self._add_button(1, 1, "\U0001F534", "Terminar sesi\u00f3n", self.end_requested)
        self._add_button(2, 0, "\U0001F9E0", "Logros", self.achievements_requested)
        self._add_button(2, 1, "\u2699\ufe0f", "Ajustes", self.settings_requested)
        self._add_button(3, 0, "\U0001F41B", "Modo desarrollador", self.developer_requested, span=2)

    def _add_button(self, row, col, icon, text, signal, span=1):
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton{background:rgba(255,255,255,0.6);border:none;border-radius:12px;}"
            "QPushButton:hover{background:rgba(255,255,255,0.8);}"
        )
        b_layout = QVBoxLayout(btn)
        b_layout.setContentsMargins(10, 10, 10, 10)
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(get_emoji_font(32))
        txt_lbl = QLabel(text)
        txt_lbl.setAlignment(Qt.AlignCenter)
        txt_lbl.setWordWrap(True)
        txt_lbl.setStyleSheet("font-size:16px;")
        b_layout.addWidget(icon_lbl)
        b_layout.addWidget(txt_lbl)
        btn.clicked.connect(signal.emit)
        if span == 1:
            self.grid.addWidget(btn, row, col)
        else:
            self.grid.addWidget(btn, row, col, 1, span)
        self.buttons.append(btn)

    def adjust_position(self):
        if not self.parent():
            return
        pw = self.parent().width()
        ph = self.parent().height()
        w = int(pw * 0.8)
        h = int(ph * 0.6)
        self.setGeometry((pw - w) // 2, (ph - h) // 2, w, h)

    def show_with_anim(self):
        self.adjust_position()
        self.opacity.setOpacity(0)
        super().show()
        self.raise_()
        anim = QPropertyAnimation(self.opacity, b"opacity", self)
        anim.setDuration(200)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        self._anim = anim

    def hide_with_anim(self):
        anim = QPropertyAnimation(self.opacity, b"opacity", self)
        anim.setDuration(200)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.finished.connect(super().hide)
        anim.finished.connect(self.close_requested)
        anim.start()
        self._anim = anim
