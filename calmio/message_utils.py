import json
from pathlib import Path
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QVariantAnimation, QColor


class MessageHandler:
    """Manage loading and display of motivational messages."""

    def __init__(self, window):
        self.window = window
        self.motivational_messages = []
        self.message_schedule = set()
        self.message_index = 0

    # ------------------------------------------------------------------
    def load_messages(self):
        path = Path(__file__).resolve().parent / "motivational_messages.json"
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.motivational_messages = data.get("messages", [])
        except Exception:
            self.motivational_messages = []

    def build_message_schedule(self, max_count: int = 150):
        schedule = []
        interval = 3
        total = 0
        while total < max_count:
            for _ in range(3):
                total += interval
                schedule.append(total)
            interval += 1
        self.message_schedule = set(schedule)

    def start_prompt_animation(self):
        self.window.message_label.setText("Toca para comenzar")
        self.window.message_label.show()
        self.window.message_container.show()
        self.window.msg_opacity.setOpacity(0.2)
        self.window.fade_anim = QPropertyAnimation(self.window.msg_opacity, b"opacity", self.window)
        self.window.fade_anim.setDuration(1500)
        self.window.fade_anim.setStartValue(0.2)
        self.window.fade_anim.setKeyValueAt(0.5, 1)
        self.window.fade_anim.setEndValue(0.2)
        self.window.fade_anim.setLoopCount(-1)
        self.window.fade_anim.start()

        self.window.bounce_anim = QVariantAnimation(self.window)
        self.window.bounce_anim.setDuration(3000)
        self.window.bounce_anim.setStartValue(14)
        self.window.bounce_anim.setKeyValueAt(0.5, 18)
        self.window.bounce_anim.setEndValue(14)
        self.window.bounce_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.window.bounce_anim.setLoopCount(-1)
        self.window.bounce_anim.valueChanged.connect(self._update_message_font)
        self.window.bounce_anim.start()

    def _update_message_font(self, value):
        font = self.window.message_label.font()
        font.setPointSize(int(value))
        self.window.message_label.setFont(font)

    def stop_prompt_animation(self):
        if hasattr(self.window, "fade_anim"):
            self.window.fade_anim.stop()
        if hasattr(self.window, "bounce_anim"):
            self.window.bounce_anim.stop()
        hide = QPropertyAnimation(self.window.msg_opacity, b"opacity", self.window)
        hide.setDuration(4000)
        hide.setStartValue(self.window.msg_opacity.opacity())
        hide.setEndValue(0)
        hide.finished.connect(self.window.message_label.hide)
        hide.start()
        self.window.fade_anim = hide

    def display_motivational_message(self, text):
        self.window.msg_opacity.setOpacity(0)
        self.window.message_label.setText(text)
        self.window.message_label.show()
        fade_in = QPropertyAnimation(self.window.msg_opacity, b"opacity", self.window)
        fade_in.setDuration(600)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_out = QPropertyAnimation(self.window.msg_opacity, b"opacity", self.window)
        fade_out.setDuration(4000)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        group = QSequentialAnimationGroup(self.window)
        group.addAnimation(fade_in)
        group.addPause(1000)
        group.addAnimation(fade_out)
        group.finished.connect(self.window.message_label.hide)
        group.start()
        self.window.temp_msg_anim = group

    def check_motivational_message(self, count):
        if count in self.message_schedule and self.motivational_messages:
            msg = self.motivational_messages[self.message_index % len(self.motivational_messages)]
            self.message_index += 1
            self.display_motivational_message(msg)
