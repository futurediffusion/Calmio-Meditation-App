from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import QWidget


class ProgressCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.seconds = 0
        # goal_step expressed in seconds (30 minute cycle)
        self.goal_step = 30 * 60
        self.setMinimumSize(220, 220)

    def set_seconds(self, s):
        self.seconds = s
        self.update()

    def paintEvent(self, event):
        if self.width() <= 0 or self.height() <= 0:
            return
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(20, 20, -20, -20)

        base_pen = QPen(QColor(200, 220, 255), 12, Qt.SolidLine, Qt.RoundCap)
        progress_pen = QPen(QColor(255, 204, 188), 12, Qt.SolidLine, Qt.RoundCap)

        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)

        progress = (self.seconds % self.goal_step) / self.goal_step
        painter.setPen(progress_pen)
        painter.drawArc(rect, 90 * 16, int(-360 * 16 * progress))
        painter.setPen(Qt.NoPen)
        fill_color = QColor(255, 204, 188, 80)
        painter.setBrush(fill_color)
        painter.drawPie(rect, 90 * 16, int(-360 * 16 * progress))

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.NoBrush)

        font = QFont("Sans Serif")
        font.setPointSize(14)
        painter.setFont(font)
        painter.setPen(QColor("#444"))

        if self.seconds < 60:
            time_str = f"{int(self.seconds)}s"
        elif self.seconds < 3600:
            m = int(self.seconds // 60)
            s = int(self.seconds % 60)
            time_str = f"{m}m" + (f" {s}s" if s else "")
        else:
            h = int(self.seconds // 3600)
            m = int((self.seconds % 3600) // 60)
            s = int(self.seconds % 60)
            parts = [f"{h}h"]
            if m:
                parts.append(f"{m}m")
            if s:
                parts.append(f"{s}s")
            time_str = " ".join(parts)

        center_text = f"{time_str}\nmeditados"
        painter.drawText(self.rect(), Qt.AlignCenter, center_text)

        base = (int(self.seconds // 60) // (self.goal_step // 60)) * (self.goal_step // 60)
        labels = {
            "top": base + (self.goal_step // 60),
            "right": base + 10,
            "left": base + 20,
        }

        label_font = QFont("Sans Serif")
        label_font.setPointSize(10)
        painter.setFont(label_font)
        painter.drawText(
            rect.center().x() - 10,
            rect.top() + 5,
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
