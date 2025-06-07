from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class WeeklyBarGraph(QWidget):
    """Simple bar graph for weekly minutes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.minutes = [0] * 7
        self.days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.setMinimumHeight(200)

    def set_minutes(self, minutes):
        self.minutes = list(minutes)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        top_margin = 20
        bottom_margin = 40
        bar_width = w / 9
        max_val = max(self.minutes) if max(self.minutes) > 0 else 1

        for i, m in enumerate(self.minutes):
            x = (i * 2 + 1) * bar_width / 2 + i * bar_width / 2
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
                str(int(m)),
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

        self.total_lbl = QLabel("Total this week: 0 min")
        self.avg_lbl = QLabel("Daily average: 0 min")
        self.longest_lbl = QLabel("Longest session: --")

        for lbl in (self.total_lbl, self.avg_lbl, self.longest_lbl):
            font = QFont("Sans Serif")
            font.setPointSize(12)
            lbl.setFont(font)
            lbl.setStyleSheet("color:#333;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)

    def set_stats(self, minutes_per_day, total, average, longest_day, longest_minutes):
        self.graph.set_minutes(minutes_per_day)
        self.total_lbl.setText(f"Total this week: {int(total)} min")
        self.avg_lbl.setText(f"Daily average: {average:.1f} min")
        if longest_day:
            self.longest_lbl.setText(
                f"Longest session: {longest_day} – {int(longest_minutes)} min"
            )
        else:
            self.longest_lbl.setText("Longest session: --")
