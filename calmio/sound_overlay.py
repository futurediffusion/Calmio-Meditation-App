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
    music_mode_changed = Signal(str)
    scale_changed = Signal(str)

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

        music_row = QHBoxLayout()
        self.music_chk = QCheckBox("\U0001F3B9 Modo m\u00fasica [OFF]")
        self.music_opts_btn = QPushButton("\u25BC")
        self.music_opts_btn.setFixedSize(20, 20)
        self.music_opts_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:14px;}"
        )
        self.music_opts_btn.clicked.connect(self._toggle_music_options)
        music_row.addWidget(self.music_chk)
        music_row.addWidget(self.music_opts_btn)
        music_row.addStretch()
        layout.addLayout(music_row)
        self.bell_chk = QCheckBox("\U0001F514 Campana cada 10 [OFF]")
        self.music_chk.toggled.connect(self.music_toggled.emit)
        self.bell_chk.toggled.connect(self.bell_toggled.emit)
        self.music_chk.toggled.connect(self._update_music_label)
        self.bell_chk.toggled.connect(self._update_bell_label)
        self._update_music_label(self.music_chk.isChecked())
        self._update_bell_label(self.bell_chk.isChecked())
        layout.addWidget(self.bell_chk)

        self.adv_widget = QWidget()
        self.adv_widget.setStyleSheet(
            "background-color:#FFFFFF;border-radius:10px;padding:10px;"
        )
        adv_layout = QVBoxLayout(self.adv_widget)
        adv_layout.setContentsMargins(10, 10, 10, 10)
        adv_layout.setSpacing(5)
        adv_layout.addWidget(QLabel("Modo musical:"))
        self.mode_group = QButtonGroup(self)
        self.mode_scale = QRadioButton("Modo normal (escala)")
        self.mode_harmonic = QRadioButton("Modo arm\u00f3nico")
        self.mode_scale.setChecked(True)
        for rb in (self.mode_scale, self.mode_harmonic):
            self.mode_group.addButton(rb)
            adv_layout.addWidget(rb)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)

        scale_row = QHBoxLayout()
        self.scale_group = QButtonGroup(self)
        self.scale_major = QRadioButton("Escala mayor")
        self.scale_minor = QRadioButton("Escala menor")
        self.scale_major.setChecked(True)
        for rb in (self.scale_major, self.scale_minor):
            self.scale_group.addButton(rb)
            scale_row.addWidget(rb)
        adv_layout.addLayout(scale_row)
        self.scale_group.buttonClicked.connect(self._on_scale_changed)

        self.adv_widget.hide()
        layout.addWidget(self.adv_widget)

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

    def _toggle_music_options(self) -> None:
        visible = self.adv_widget.isVisible()
        self.adv_widget.setVisible(not visible)
        self.music_opts_btn.setText("\u25B2" if not visible else "\u25BC")

    def _on_mode_changed(self) -> None:
        mode = "harmonic" if self.mode_harmonic.isChecked() else "scale"
        self.music_mode_changed.emit(mode)

    def _on_scale_changed(self) -> None:
        scale = "minor" if self.scale_minor.isChecked() else "major"
        self.scale_changed.emit(scale)

    def set_music_mode(self, mode: str) -> None:
        if mode == "harmonic":
            self.mode_harmonic.setChecked(True)
        else:
            self.mode_scale.setChecked(True)

    def set_scale_type(self, scale: str) -> None:
        if scale == "minor":
            self.scale_minor.setChecked(True)
        else:
            self.scale_major.setChecked(True)

