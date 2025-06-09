from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QCheckBox,
)


class OptionsOverlay(QWidget):
    """Simple configuration overlay with data reset option."""

    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color:#FAFAFA;color:#444;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header = QHBoxLayout()
        self.back_btn = QPushButton("\u2190")
        self.back_btn.setStyleSheet(
            "QPushButton{background:none;border:none;font-size:18px;}"
        )
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        title = QLabel("Configuraci\u00f3n")
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Medium)
        title.setFont(t_font)
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title, alignment=Qt.AlignCenter)
        header.addStretch()
        layout.addLayout(header)

        self.dark_chk = QCheckBox("Modo oscuro")
        self.dark_chk.setStyleSheet("font-size:14px;")
        store = getattr(parent, "data_store", None)
        if store:
            self.dark_chk.setChecked(store.get_visual_setting("dark_mode", False))
        self.dark_chk.stateChanged.connect(self._dark_mode_changed)
        layout.addWidget(self.dark_chk, alignment=Qt.AlignLeft)

        self.reset_btn = QPushButton("Borrar todos los datos")
        self.reset_btn.setStyleSheet(
            "QPushButton{" "background-color:#CCE4FF;border:none;border-radius:20px;"
            "padding:12px 24px;font-size:14px;}"
        )
        self.reset_btn.clicked.connect(self.confirm_reset)
        layout.addWidget(self.reset_btn, alignment=Qt.AlignCenter)

        layout.addStretch()

    def _dark_mode_changed(self, state: int) -> None:
        is_dark = state == Qt.Checked
        parent = self.parent()
        store = getattr(parent, "data_store", None)
        if store:
            store.set_visual_setting("dark_mode", is_dark)
        if hasattr(parent, "bg"):
            parent.bg.set_dark_mode(is_dark)

    def confirm_reset(self):
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "\u00bfEst\u00e1s seguro de borrar todos los datos?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            store = getattr(self.parent(), "data_store", None)
            if store:
                store.clear_data()
            if hasattr(self.parent(), "stats_overlay"):
                self.parent().stats_overlay.update_minutes(0)
                self.parent().stats_overlay.update_streak(0)
                self.parent().stats_overlay.update_last_session("", 0, 0, 0, 0, [])
                self.parent().stats_overlay.update_badges({})
            self.parent().meditation_seconds = 0
            QMessageBox.information(self, "Listo", "Datos borrados")
