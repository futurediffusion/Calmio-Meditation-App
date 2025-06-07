from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import QWidget


class ProgressCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.minutes = 0
        self.goal_step = 30
        self.setMinimumSize(220, 220)

    def set_minutes(self, m):
        self.minutes = m
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(20, 20, -20, -20)

        base_pen = QPen(QColor(200, 220, 255), 12, Qt.SolidLine, Qt.RoundCap)
        progress_pen = QPen(QColor(255, 204, 188), 12, Qt.SolidLine, Qt.RoundCap)

        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)

        progress = (self.minutes % self.goal_step) / self.goal_step
        painter.setPen(progress_pen)
        painter.drawArc(rect, 90 * 16, int(-360 * 16 * progress))

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.NoBrush)

        font = QFont("Sans Serif")
        font.setPointSize(14)
        painter.setFont(font)
        painter.setPen(QColor("#444"))
        center_text = f"{self.minutes} min\nmeditated"
        painter.drawText(self.rect(), Qt.AlignCenter, center_text)

        base = (self.minutes // self.goal_step) * self.goal_step
        labels = {
            "top": base + self.goal_step,
            "right": base + 10,
            "left": base + 20,
        }

        label_font = QFont("Sans Serif")
        label_font.setPointSize(10)
        painter.setFont(label_font)
        painter.drawText(
            rect.center().x() - 10,
            rect.top() - 5,
            f"{labels['top']} min",
        )
        painter.drawText(
            rect.right() - 40,
            rect.bottom() + 15,
            f"{labels['right']} min",
        )
        painter.drawText(
            rect.left() + 10,
            rect.bottom() + 15,
            f"{labels['left']} min",
        )
