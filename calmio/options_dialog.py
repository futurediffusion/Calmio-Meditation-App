from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox


class OptionsDialog(QDialog):
    def __init__(self, parent=None, data_store=None):
        super().__init__(parent)
        self.setWindowTitle("Opciones")
        self.data_store = data_store
        layout = QVBoxLayout(self)
        self.clear_btn = QPushButton("Borrar todos los datos")
        self.clear_btn.clicked.connect(self.confirm_clear)
        layout.addWidget(self.clear_btn)
        self.setLayout(layout)

    def confirm_clear(self):
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Estás seguro de borrar todos los datos?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes and self.data_store is not None:
            if hasattr(self.data_store, "reset"):
                self.data_store.reset()
            else:
                # Fallback: delete file and reload
                self.data_store.path.unlink(missing_ok=True)
                self.data_store.load()

