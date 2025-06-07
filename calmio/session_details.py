from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QPainterPath, QLinearGradient, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame, QGraphicsDropShadowEffect


class BreathGraph(QWidget):
    """Simple line graph to display breathing cycle durations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cycles = []
        self.setMinimumHeight(200)
        self.start_label = ""
        self.end_label = ""

    def set_cycles(self, cycles):
        self.cycles = list(cycles or [])
        if self.cycles:
            self.start_label = f"Inicio: {self.cycles[0]:.0f}s"
            self.end_label = f"\u00DAltima: {self.cycles[-1]:.0f}s"
        self.update()

    def paintEvent(self, event):
        if not self.cycles:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        margin_x = 40
        margin_y = 20
        w = self.width() - 2 * margin_x
        h = self.height() - 2 * margin_y

        min_v = min(self.cycles)
        max_v = max(self.cycles)
        span = max(max_v - min_v, 1e-6)

        step_x = w / (len(self.cycles) - 1)
        points = []
        for i, v in enumerate(self.cycles):
            x = margin_x + i * step_x
            y = margin_y + h - ((v - min_v) / span * h)
            points.append(QPointF(x, y))

        path = QPainterPath(points[0])
        for p in points[1:]:
            path.lineTo(p)

        fill = QPainterPath(path)
        fill.lineTo(points[-1].x(), self.height() - margin_y)
        fill.lineTo(points[0].x(), self.height() - margin_y)
        fill.closeSubpath()

        grad = QLinearGradient(0, margin_y, 0, self.height() - margin_y)
        col = QColor(173, 216, 230)
        grad.setColorAt(0, QColor(col.red(), col.green(), col.blue(), 120))
        grad.setColorAt(1, QColor(col.red(), col.green(), col.blue(), 40))
        painter.fillPath(fill, QBrush(grad))

        pen = QPen(col, 2)
        painter.setPen(pen)
        painter.drawPath(path)

        lbl_font = QFont("Sans Serif")
        lbl_font.setPointSize(10)
        painter.setFont(lbl_font)
        painter.setPen(QColor("#555"))
        painter.drawText(points[0].x() - 20, points[0].y() - 5, self.start_label)
        painter.drawText(points[-1].x() - 30, points[-1].y() - 5, self.end_label)


class SessionDetailsView(QWidget):
    """View showing detailed breathing data for a session."""

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
        self.back_btn.setStyleSheet("QPushButton{background:none;border:none;font-size:18px;}")
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        title = QLabel("Detalles de la sesi\u00F3n")
        t_font = QFont("Sans Serif")
        t_font.setPointSize(20)
        t_font.setWeight(QFont.Medium)
        title.setFont(t_font)
        title.setAlignment(Qt.AlignCenter)
        header.addWidget(title, alignment=Qt.AlignCenter)
        header.addStretch()
        layout.addLayout(header)

        self.summary = QLabel("")
        self.summary.setAlignment(Qt.AlignCenter)
        self.summary.setStyleSheet("background:#CCE4FF;border-radius:20px;padding:8px 12px;font-size:14px;")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        self.summary.setGraphicsEffect(shadow)
        layout.addWidget(self.summary, alignment=Qt.AlignCenter)

        self.graph = BreathGraph(self)
        layout.addWidget(self.graph)

        self.phrase = QLabel("Tu respiraci\u00F3n se profundiz\u00F3 progresivamente.")
        ph_font = QFont("Sans Serif")
        ph_font.setPointSize(12)
        self.phrase.setFont(ph_font)
        self.phrase.setAlignment(Qt.AlignCenter)
        self.phrase.setStyleSheet("color:#666;")
        layout.addWidget(self.phrase, alignment=Qt.AlignCenter)

    def set_session(self, session):
        start = session.get("start", "").split(" ")[-1]
        duration = session.get("duration", 0)
        breaths = session.get("breaths", 0)
        cycles = session.get("cycles", [])
        last_cycle = cycles[-1] if cycles else session.get("last_inhale", 0) + session.get("last_exhale", 0)

        if duration < 60:
            dur_str = f"{duration:.0f}s"
        else:
            m = int(duration // 60)
            s = int(duration % 60)
            dur_str = f"{m}m" + (f" {s}s" if s else "")
        self.summary.setText(f"{start} \u2022 {dur_str} \u2022 {breaths} br \u2022 {last_cycle:.0f}s \u00FAltima")

        self.graph.set_cycles(cycles)
