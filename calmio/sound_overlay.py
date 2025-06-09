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
    music_volume_changed = Signal(int)
    drop_volume_changed = Signal(int)
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

        self.music_chk = QCheckBox("\U0001F3B9 Modo m\u00fasica [OFF]")
        self.bell_chk = QCheckBox("\U0001F514 Campana cada 10 [OFF]")
        self.music_chk.toggled.connect(self.music_toggled.emit)
        self.bell_chk.toggled.connect(self.bell_toggled.emit)
        self.music_chk.toggled.connect(self._update_music_label)
        self.bell_chk.toggled.connect(self._update_bell_label)
        self._update_music_label(self.music_chk.isChecked())
        self._update_bell_label(self.bell_chk.isChecked())
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

        layout.addWidget(QLabel("Volumen m\u00fasica"))
        self.music_slider = QSlider(Qt.Horizontal)
        self.music_slider.setRange(0, 100)
        self.music_slider.setValue(50)
        self.music_slider.valueChanged.connect(self.music_volume_changed.emit)
        layout.addWidget(self.music_slider)

        layout.addWidget(QLabel("Volumen drop"))
        self.drop_slider = QSlider(Qt.Horizontal)
        self.drop_slider.setRange(0, 100)
        self.drop_slider.setValue(50)
        self.drop_slider.valueChanged.connect(self.drop_volume_changed.emit)
        layout.addWidget(self.drop_slider)

        self.mute_btn = QPushButton("Silenciar todo")
        self.mute_btn.setStyleSheet(
            "QPushButton{" "background-color:#CCE4FF;border:none;border-radius:20px;"
            "padding:12px 24px;font-size:14px;}"
        )
        self.mute_btn.clicked.connect(self.mute_all.emit)
        layout.addWidget(self.mute_btn, alignment=Qt.AlignCenter)

        layout.addStretch()

    def _update_music_label(self, checked: bool) -> None:
        state = "ON" if checked else "OFF"
        self.music_chk.setText(f"\U0001F3B9 Modo m\u00fasica [{state}]")

    def _update_bell_label(self, checked: bool) -> None:
        state = "ON" if checked else "OFF"
        self.bell_chk.setText(f"\U0001F514 Campana cada 10 [{state}]")

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

