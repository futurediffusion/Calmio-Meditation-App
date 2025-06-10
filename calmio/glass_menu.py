from PySide6.QtCore import Qt, Signal, QPropertyAnimation
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGraphicsOpacityEffect,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)

from .font_utils import get_emoji_font


class GlassMenu(QWidget):
    """Minimal floating menu with a glass style background."""

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
        layout.setSpacing(15)

        header = QHBoxLayout()
        self.back_btn = QPushButton("\u2190")
        self.back_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;}"
        )
        self.back_btn.clicked.connect(self.hide_with_anim)
        header.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        title = QLabel("Men\u00fa")
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Medium)
        title.setFont(t_font)
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title, alignment=Qt.AlignCenter)
        header.addStretch()
        layout.addLayout(header)

        self.cards = []
        self.labels = []
        self._add_menu_row("\U0001FAC1", "Respiraciones", self.breath_modes_requested)
        self._add_menu_row("\U0001F3B5", "Sonido", self.sound_requested)
        self._add_menu_row("\U0001F4CA", "Estad\u00edsticas", self.stats_requested)
        self._add_menu_row("\U0001F534", "Terminar sesi\u00f3n", self.end_requested)
        self._add_menu_row("\U0001F9E0", "Logros", self.achievements_requested)
        self._add_menu_row("\u2699\ufe0f", "Ajustes", self.settings_requested)
        self._add_menu_row("\U0001F41B", "Modo desarrollador", self.developer_requested)
        layout.addStretch()

    def _add_menu_row(self, icon: str, text: str, signal: Signal) -> None:
        card = QFrame()
        card.setObjectName("menuCard")
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(
            "QFrame#menuCard{background:white;border-radius:15px;}"
            "QFrame#menuCard:hover{background:#F2F2F2;}"
        )
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(8)
        eff.setOffset(0, 2)
        card.setGraphicsEffect(eff)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(get_emoji_font(18))
        icon_lbl.setAlignment(Qt.AlignCenter)

        txt_lbl = QLabel(text)
        name_font = QFont("Sans Serif")
        name_font.setPointSize(14)
        name_font.setWeight(QFont.Bold)
        txt_lbl.setFont(name_font)
        txt_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(icon_lbl)
        layout.addWidget(txt_lbl)

        card.mouseReleaseEvent = lambda e, s=signal: s.emit()

        self.layout().addWidget(card)
        self.cards.append(card)
        self.labels.append(txt_lbl)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        max_w = int(self.width() * 0.9)
        font_size = 12 if self.width() < 400 else 14
        for card in self.cards:
            card.setMaximumWidth(max_w)
        for lbl in self.labels:
            f = lbl.font()
            f.setPointSize(font_size)
            lbl.setFont(f)

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
