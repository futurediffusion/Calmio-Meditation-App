from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


def format_duration(minutes: float) -> str:
    """Return a human friendly time string for the given minutes."""
    if minutes >= 60:
        h = int(minutes // 60)
        m = int(minutes % 60)
        return f"{h}h" + (f" {m}m" if m else "")
    if minutes >= 1:
        return f"{int(minutes)}m"
    secs = int(round(minutes * 60))
    return f"{secs}s"


class WeeklyBarGraph(QWidget):
    """Simple bar graph for weekly minutes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.minutes = [0] * 7
        self.days = ["Lun", "Mar", "Mi\u00e9", "Jue", "Vie", "S\u00e1b", "Dom"]
        self.setMinimumHeight(200)

    def set_minutes(self, minutes):
        self.minutes = list(minutes)
        self.update()

    def paintEvent(self, event):
        if self.width() <= 0 or self.height() <= 0:
            return
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        top_margin = 20
        bottom_margin = 40
        n = len(self.minutes)
        bar_width = w / (1.5 * n)
        max_val = max(self.minutes) if max(self.minutes) > 0 else 1

        for i, m in enumerate(self.minutes):
            x = ((3 * i + 1) / 2) * bar_width
            bar_h = (m / max_val) * (h - top_margin - bottom_margin)
            y = h - bottom_margin - bar_h
            color = QColor("#CBE8F4") if i % 2 == 0 else QColor("#FADDCB")
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            rect = QRectF(x, y, bar_width, bar_h)
            painter.drawRoundedRect(rect, 4, 4)

            painter.setPen(QColor("#333"))
            font = QFont("Sans Serif")
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(
                QRectF(x, y - 18, bar_width, 16),
                Qt.AlignHCenter | Qt.AlignBottom,
                format_duration(m),
            )
            painter.drawText(
                QRectF(x, h - bottom_margin, bar_width, bottom_margin),
                Qt.AlignHCenter | Qt.AlignTop,
                self.days[i],
            )


class WeeklyStatsView(QWidget):
    """Widget displaying weekly statistics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        self.graph = WeeklyBarGraph(self)
        layout.addWidget(self.graph)

        self.total_lbl = QLabel("Total esta semana: 0 min")
        self.avg_lbl = QLabel("Promedio diario: 0 min")
        self.longest_lbl = QLabel("Sesi\u00f3n m\u00e1s larga: --")

        for lbl in (self.total_lbl, self.avg_lbl, self.longest_lbl):
            font = QFont("Sans Serif")
            font.setPointSize(12)
            lbl.setFont(font)
            lbl.setStyleSheet("color:#333;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)

    def set_stats(self, minutes_per_day, total, average, longest_day, longest_time, longest_minutes):
        self.graph.set_minutes(minutes_per_day)
        self.total_lbl.setText(f"Total esta semana: {format_duration(total)}")
        self.avg_lbl.setText(f"Promedio diario: {format_duration(average)}")
        if longest_day:
            self.longest_lbl.setText(
                f"Sesi\u00f3n m\u00e1s larga: {longest_day} {longest_time} – {format_duration(longest_minutes)}"
            )
        else:
            self.longest_lbl.setText("Sesi\u00f3n m\u00e1s larga: --")
