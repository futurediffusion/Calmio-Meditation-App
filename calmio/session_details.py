from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import (
    QFont,
    QPainter,
    QColor,
    QPen,
    QPainterPath,
    QLinearGradient,
    QBrush,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QGraphicsDropShadowEffect,
)


class BreathGraph(QWidget):
    """Smooth graph representing inhale and exhale durations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cycles = []
        self.values = []
        self.setMinimumHeight(200)
        self.start_label = ""
        self.end_label = ""

    def set_cycles(self, cycles):
        self.cycles = list(cycles or [])
        self.values = []
        if self.cycles and isinstance(self.cycles[0], dict):
            for c in self.cycles:
                # start from baseline then rise on inhale and fall on exhale
                self.values.extend([
                    0.0,
                    float(c.get("inhale", 0)),
                    0.0,
                    float(c.get("exhale", 0)),
                ])
            self.values.append(0.0)
        else:
            self.values = [float(v) for v in self.cycles]
        if self.values:
            if self.cycles and isinstance(self.cycles[0], dict):
                start_dur = self.cycles[0].get("inhale", 0) + self.cycles[0].get("exhale", 0)
                end_dur = self.cycles[-1].get("inhale", 0) + self.cycles[-1].get("exhale", 0)
            else:
                start_dur = self.values[1] if len(self.values) > 3 else 0
                end_dur = self.values[-2] if len(self.values) > 3 else 0
            self.start_label = f"Inicio: {start_dur:.2f}s"
            self.end_label = f"\u00DAltima: {end_dur:.2f}s"
        self.update()

    def _smooth_path(self, pts):
        path = QPainterPath(pts[0])
        for i in range(1, len(pts) - 1):
            mid = QPointF(
                (pts[i].x() + pts[i + 1].x()) / 2,
                (pts[i].y() + pts[i + 1].y()) / 2,
            )
            path.quadTo(pts[i], mid)
        path.quadTo(pts[-1], pts[-1])
        return path

    def paintEvent(self, event):
        if not self.values:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        margin_x = 40
        margin_y = 20
        w = self.width() - 2 * margin_x
        h = self.height() - 2 * margin_y

        min_v = min(self.values)
        max_v = max(self.values)
        span = max(max_v - min_v, 1e-6)

        step_x = w / (len(self.values) - 1)
        points = []
        for i, v in enumerate(self.values):
            x = margin_x + i * step_x
            y = margin_y + h - ((v - min_v) / span * h)
            points.append(QPointF(x, y))

        path = self._smooth_path(points)

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

        self.summary = QFrame()
        self.summary.setStyleSheet(
            "background:#E0F0FF;border-radius:20px;padding:6px;"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        self.summary.setGraphicsEffect(shadow)

        sum_layout = QVBoxLayout()
        sum_layout.setContentsMargins(12, 4, 12, 4)
        sum_layout.setSpacing(6)
        self.summary.setLayout(sum_layout)

        line1 = QHBoxLayout()
        line1.setContentsMargins(0, 0, 0, 0)
        line1.setSpacing(8)

        line2 = QHBoxLayout()
        line2.setContentsMargins(0, 0, 0, 0)
        line2.setSpacing(8)

        def pair(icon: str):
            ic = QLabel(icon)
            ic.setStyleSheet("font-size:12px;color:#555;")
            val = QLabel("-")
            val.setStyleSheet("font-size:12px;color:#000;")
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(4)
            row.addWidget(ic)
            row.addWidget(val)
            w = QWidget()
            w.setLayout(row)
            return w, val

        self.start_w, self.start_lbl = pair("\u23F0")
        self.dur_w, self.dur_lbl = pair("\u23F1")
        self.breath_w, self.breath_lbl = pair("\U0001FAC1")
        self.first_w, self.first_lbl = pair("\u2B06\ufe0f")
        self.last_w, self.last_lbl = pair("\u2B07\ufe0f")

        for w in (self.start_w, self.dur_w, self.breath_w):
            line1.addWidget(w)
        line1.addStretch()

        for w in (self.first_w, self.last_w):
            line2.addWidget(w)
        line2.addStretch()

        self.tag_lbl = QLabel("\u00DAltima sesi\u00F3n")
        self.tag_lbl.setStyleSheet(
            "background:#eee;border-radius:10px;padding:2px 6px;font-size:10px;color:#777;"
        )
        line2.addWidget(self.tag_lbl)
        self.tag_lbl.hide()

        sum_layout.addLayout(line1)
        sum_layout.addLayout(line2)

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

    def set_session(self, session, is_last=False):
        start = session.get("start", "").split(" ")[-1]
        duration = session.get("duration", 0)
        breaths = session.get("breaths", 0)
        cycles = session.get("cycles", [])
        if not cycles and session.get("last_inhale") is not None:
            cycles = [
                {
                    "inhale": session.get("last_inhale", 0),
                    "exhale": session.get("last_exhale", 0),
                }
            ]

        first_cycle = cycles[0] if cycles and isinstance(cycles[0], dict) else {}
        last_cycle = cycles[-1] if cycles and isinstance(cycles[-1], dict) else {}
        first_duration = first_cycle.get("inhale", 0) + first_cycle.get("exhale", 0)
        last_duration = last_cycle.get("inhale", 0) + last_cycle.get("exhale", 0)

        if duration < 60:
            dur_str = f"{duration:.0f}s"
        else:
            m = int(duration // 60)
            s = int(duration % 60)
            dur_str = f"{m}m" + (f" {s}s" if s else "")

        self.start_lbl.setText(start)
        self.dur_lbl.setText(dur_str)
        self.breath_lbl.setText(str(breaths))
        self.first_lbl.setText(f"{first_duration:.2f}s")
        self.last_lbl.setText(f"{last_duration:.2f}s")
        self.tag_lbl.setVisible(is_last)

        self.graph.set_cycles(cycles)
