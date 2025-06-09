from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QInputDialog,
)
from PySide6.QtGui import QFont
import json
from pathlib import Path


class MantrasOverlay(QWidget):
    """Overlay to view and edit motivational messages."""

    back_requested = Signal()

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

        title = QLabel("Mantras")
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Medium)
        title.setFont(t_font)
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title, alignment=Qt.AlignCenter)
        header.addStretch()
        layout.addLayout(header)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Agregar")
        self.del_btn = QPushButton("Eliminar")
        self.add_btn.clicked.connect(self._add_message)
        self.del_btn.clicked.connect(self._del_message)
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._load_messages()

    # -------------------------------------------------------------
    def _messages_file(self) -> Path:
        return Path(__file__).resolve().parent / "motivational_messages.json"

    def _load_messages(self):
        handler = getattr(self.parent(), "message_handler", None)
        msgs = []
        if handler:
            msgs = handler.motivational_messages
        if not msgs:
            try:
                data = json.loads(self._messages_file().read_text(encoding="utf-8"))
                msgs = data.get("messages", [])
            except Exception:
                msgs = []
        for m in msgs:
            self.list_widget.addItem(m)

    def _save_messages(self):
        handler = getattr(self.parent(), "message_handler", None)
        msgs = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        if handler:
            handler.motivational_messages = msgs
        try:
            with self._messages_file().open("w", encoding="utf-8") as f:
                json.dump({"messages": msgs}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _add_message(self):
        text, ok = QInputDialog.getText(self, "Nuevo mantra", "Texto:")
        if ok and text.strip():
            self.list_widget.addItem(text.strip())
            self._save_messages()

    def _del_message(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.list_widget.takeItem(row)
            self._save_messages()
