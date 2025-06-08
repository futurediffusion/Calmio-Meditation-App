from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QSlider,
)


class SoundOverlay(QWidget):
    """Overlay to configure optional background sounds."""

    back_requested = Signal()
    environment_changed = Signal(str)
    music_toggled = Signal(bool)
    bell_toggled = Signal(bool)
    volume_changed = Signal(int)
    bell_volume_changed = Signal(int)
    mute_all = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color:#FAFAFA;border-radius:20px;color:#444;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header = QHBoxLayout()
        self.back_btn = QPushButton("\u2190")
        self.back_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;}"
        )
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        title = QLabel("Sonido")
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Medium)
        title.setFont(t_font)
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title, alignment=Qt.AlignCenter)
        header.addStretch()
        layout.addLayout(header)

        layout.addWidget(QLabel("Tipo de fondo sonoro:"))
        self.env_group = QButtonGroup(self)
        self.env_none = QRadioButton("Ninguno")
        self.env_none.setChecked(True)
        self.env_bosque = QRadioButton("Bosque")
        self.env_lluvia = QRadioButton("Lluvia")
        self.env_fuego = QRadioButton("Fuego")
        self.env_mar = QRadioButton("Mar")
        for rb in (
            self.env_none,
            self.env_bosque,
            self.env_lluvia,
            self.env_fuego,
            self.env_mar,
        ):
            self.env_group.addButton(rb)
            layout.addWidget(rb)
        self.env_group.buttonClicked.connect(self._on_env_changed)

        self.music_chk = QCheckBox("Modo m\u00fasica")
        self.bell_chk = QCheckBox("Campana cada 10 respiraciones")
        self.music_chk.toggled.connect(self.music_toggled.emit)
        self.bell_chk.toggled.connect(self.bell_toggled.emit)
        layout.addWidget(self.music_chk)
        layout.addWidget(self.bell_chk)

        layout.addWidget(QLabel("Volumen general"))
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        self.vol_slider.valueChanged.connect(self.volume_changed.emit)
        layout.addWidget(self.vol_slider)

        layout.addWidget(QLabel("Volumen campana"))
        self.bell_slider = QSlider(Qt.Horizontal)
        self.bell_slider.setRange(0, 100)
        self.bell_slider.setValue(50)
        self.bell_slider.valueChanged.connect(self.bell_volume_changed.emit)
        layout.addWidget(self.bell_slider)

        self.mute_btn = QPushButton("Silenciar todo")
        self.mute_btn.setStyleSheet(
            "QPushButton{" "background-color:#CCE4FF;border:none;border-radius:20px;"
            "padding:12px 24px;font-size:14px;}"
        )
        self.mute_btn.clicked.connect(self.mute_all.emit)
        layout.addWidget(self.mute_btn, alignment=Qt.AlignCenter)

        layout.addStretch()

    def _on_env_changed(self):
        if self.env_bosque.isChecked():
            env = "bosque"
        elif self.env_lluvia.isChecked():
            env = "lluvia"
        elif self.env_fuego.isChecked():
            env = "fuego"
        elif self.env_mar.isChecked():
            env = "mar"
        else:
            env = "none"
        self.environment_changed.emit(env)

