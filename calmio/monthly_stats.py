from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPainterPath, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout


class MonthlyLineGraph(QWidget):
    """Smooth line graph for weekly minutes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.minutes = []
        self.labels = ["Week 1", "Week 2", "Week 3", "Week 4/5"]
        self.setMinimumHeight(200)

    def set_minutes(self, minutes):
        self.minutes = list(minutes)
        self.update()

    def paintEvent(self, event):
        if not self.minutes:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        margin = 30
        step = (w - 2 * margin) / (len(self.minutes) - 1)
        max_val = max(self.minutes) if max(self.minutes) > 0 else 1
        points = []
        for i, m in enumerate(self.minutes):
            x = margin + i * step
            y = margin + (1 - m / max_val) * (h - 2 * margin)
            points.append((x, y))

        path = QPainterPath()
        path.moveTo(*points[0])
        for i in range(1, len(points)):
            x1, y1 = points[i - 1]
            x2, y2 = points[i]
            cx1 = x1 + step / 2
            cx2 = x2 - step / 2
            path.cubicTo(cx1, y1, cx2, y2, x2, y2)

        fill_path = QPainterPath(path)
        fill_path.lineTo(points[-1][0], h - margin)
        fill_path.lineTo(points[0][0], h - margin)
        fill_path.closeSubpath()

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#D7DFF6"))
        painter.drawPath(fill_path)

        pen = QPen(QColor("#8D9DFE"), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        label_font = QFont("Sans Serif")
        label_font.setPointSize(10)
        painter.setFont(label_font)
        painter.setPen(QColor("#555"))
        for i, (x, _) in enumerate(points):
            painter.drawText(
                QRectF(x - step / 2, h - margin + 4, step, margin - 4),
                Qt.AlignHCenter | Qt.AlignTop,
                self.labels[i],
            )


class DonutProgress(QWidget):
    """Circular progress bar for monthly goal."""

    def __init__(self, goal=600, parent=None):
        super().__init__(parent)
        self.goal = goal
        self.minutes = 0
        self.setMinimumSize(140, 140)

    def set_goal(self, goal):
        self.goal = goal
        self.update()

    def set_minutes(self, minutes):
        self.minutes = minutes
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)
        base_pen = QPen(QColor("#E0E0E0"), 12, Qt.SolidLine, Qt.RoundCap)
        progress_pen = QPen(QColor("#8D9DFE"), 12, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)
        progress = min(self.minutes / self.goal, 1.0) if self.goal else 0
        painter.setPen(progress_pen)
        painter.drawArc(rect, 90 * 16, int(-360 * 16 * progress))

        font = QFont("Sans Serif")
        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(QColor("#444"))
        center_text = f"{int(self.minutes)}\n/{int(self.goal)} min"
        painter.drawText(self.rect(), Qt.AlignCenter, center_text)


class MonthlyStatsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.graph = MonthlyLineGraph(self)
        layout.addWidget(self.graph)

        bottom = QHBoxLayout()
        bottom.setSpacing(20)
        layout.addLayout(bottom)

        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(6)
        bottom.addLayout(stats_layout)
        bottom.addStretch()

        lbl_font = QFont("Sans Serif")
        lbl_font.setPointSize(12)

        self.total_lbl = QLabel("Total meditated:\n0 min")
        self.avg_lbl = QLabel("Daily avg:\n0 min")
        self.best_lbl = QLabel("Best week:\n--")
        self.streak_lbl = QLabel("Longest streak: 0 days")

        for lbl in (self.total_lbl, self.avg_lbl, self.best_lbl, self.streak_lbl):
            lbl.setFont(lbl_font)
            lbl.setStyleSheet("color:#444;")
            stats_layout.addWidget(lbl)

        self.progress = DonutProgress()
        bottom.addWidget(self.progress, alignment=Qt.AlignRight)

    def set_stats(self, weekly_minutes, total, average, best_week_idx, longest_streak, goal=600):
        self.graph.set_minutes(weekly_minutes)
        self.total_lbl.setText(f"Total meditated\n{int(total)} min")
        self.avg_lbl.setText(f"Daily avg\n{average:.1f} min")
        self.best_lbl.setText(f"Best week\nWeek {best_week_idx} - {int(max(weekly_minutes))} min")
        self.streak_lbl.setText(f"Longest streak: {longest_streak} days")
        self.progress.set_goal(goal)
        self.progress.set_minutes(total)

