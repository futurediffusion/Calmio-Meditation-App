from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class DeveloperOverlay(QWidget):
    """Small menu for developer options."""

    speed_toggled = Signal()
    next_day_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color:#FAFAFA;border-radius:10px;"
            "border:1px solid #ccc;"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.speed_btn = QPushButton("\u26A1")
        self.day_btn = QPushButton("\u23E9")
        for btn in (self.speed_btn, self.day_btn):
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                "QPushButton{background:white;border:none;font-size:20px;}"
            )
            btn.setFocusPolicy(Qt.NoFocus)

        self.speed_btn.clicked.connect(self.speed_toggled.emit)
        self.day_btn.clicked.connect(self.next_day_requested.emit)

        layout.addWidget(self.speed_btn)
        layout.addWidget(self.day_btn)
