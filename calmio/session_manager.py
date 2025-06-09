import time
from PySide6.QtCore import QEasingCurve, QAbstractAnimation, QPropertyAnimation, QVariantAnimation


class SessionManager:
    """Session timing and animation logic extracted from MainWindow."""

    def __init__(self, window):
        self.window = window

    # ------------------------------------------------------------------
    def update_timer(self):
        if self.window.session_active and self.window.circle.phase != 'idle':
            self.window.meditation_seconds += 1
            self.window.session_seconds += 1
            self.window.stats_overlay.update_minutes(self.window.meditation_seconds)

    def start_waves(self, center, color):
        if hasattr(self.window, "wave_overlay"):
            self.window.wave_overlay.start_waves(center, color)

    def on_breath_start(self, color, duration):
        if not self.window.session_active:
            self.window.session_active = True
            self.window.session_start = self.window.data_store.now()
            self.window.session_seconds = 0
            self.window.cycle_durations = []
            self.window.stop_prompt_animation()
            self.window._chakra_index = 0
            if hasattr(self.window, "bg"):
                self.window.bg.transition_to_index(0, duration=0)
        self.window.cycle_start = time.perf_counter()

        if (
            hasattr(self.window, "count_anim")
            and self.window.count_anim.state() != QAbstractAnimation.Stopped
        ):
            self.window.count_anim.stop()

        self.window.label.setText(str(self.window.circle.breath_count + 1))
        self.window.count_opacity.setOpacity(0)
        self.window.count_anim = QPropertyAnimation(self.window.count_opacity, b"opacity", self.window)
        self.window.count_anim.setDuration(int(duration))
        self.window.count_anim.setStartValue(0)
        self.window.count_anim.setEndValue(1)
        self.window.count_anim.start()

        if self.window.text_color_anim and self.window.text_color_anim.state() != QAbstractAnimation.Stopped:
            self.window.text_color_anim.stop()
        self.window.text_color_anim = QVariantAnimation(self.window)
        self.window.text_color_anim.setDuration(int(duration))
        self.window.text_color_anim.setStartValue(self.window.current_text_color)
        self.window.text_color_anim.setEndValue(color)
        self.window.text_color_anim.valueChanged.connect(self.window._update_label_color)
        self.window.text_color_anim.start()

        if hasattr(self.window, "bg_anim") and self.window.bg_anim.state() != QAbstractAnimation.Stopped:
            self.window.bg_anim.stop()
        self.window.bg_anim = QPropertyAnimation(self.window.bg, b"opacity", self.window)
        self.window.bg_anim.setDuration(int(duration))
        self.window.bg_anim.setStartValue(self.window.bg.opacity)
        self.window.bg_anim.setEndValue(1.0)
        self.window.bg_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.window.bg_anim.start()

        if hasattr(self.window, "bg_padding_anim") and self.window.bg_padding_anim.state() != QAbstractAnimation.Stopped:
            self.window.bg_padding_anim.stop()
        self.window.bg_padding_anim = QPropertyAnimation(self.window.bg, b"ring_padding", self.window)
        self.window.bg_padding_anim.setDuration(int(duration))
        self.window.bg_padding_anim.setStartValue(self.window.bg.ring_padding)
        self.window.bg_padding_anim.setEndValue(1.25)
        self.window.bg_padding_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.window.bg_padding_anim.start()

        if hasattr(self.window, "sound_manager"):
            self.window.sound_manager.breath_inhale(int(duration))

    def on_exhale_start(self, duration, color):
        if (
            hasattr(self.window, "count_anim")
            and self.window.count_anim.state() != QAbstractAnimation.Stopped
        ):
            self.window.count_anim.stop()

        self.window.count_anim = QPropertyAnimation(self.window.count_opacity, b"opacity", self.window)
        self.window.count_anim.setDuration(int(duration))
        self.window.count_anim.setStartValue(self.window.count_opacity.opacity())
        self.window.count_anim.setEndValue(0)
        self.window.count_anim.start()

        if self.window.text_color_anim and self.window.text_color_anim.state() != QAbstractAnimation.Stopped:
            self.window.text_color_anim.stop()
        self.window.text_color_anim = QVariantAnimation(self.window)
        self.window.text_color_anim.setDuration(int(duration))
        self.window.text_color_anim.setStartValue(self.window.current_text_color)
        self.window.text_color_anim.setEndValue(color)
        self.window.text_color_anim.valueChanged.connect(self.window._update_label_color)
        self.window.text_color_anim.start()

        if hasattr(self.window, "bg_anim") and self.window.bg_anim.state() != QAbstractAnimation.Stopped:
            self.window.bg_anim.stop()
        self.window.bg_anim = QPropertyAnimation(self.window.bg, b"opacity", self.window)
        self.window.bg_anim.setDuration(int(duration))
        self.window.bg_anim.setStartValue(self.window.bg.opacity)
        self.window.bg_anim.setEndValue(0.0)
        self.window.bg_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.window.bg_anim.start()

        if hasattr(self.window, "bg_padding_anim") and self.window.bg_padding_anim.state() != QAbstractAnimation.Stopped:
            self.window.bg_padding_anim.stop()
        self.window.bg_padding_anim = QPropertyAnimation(self.window.bg, b"ring_padding", self.window)
        self.window.bg_padding_anim.setDuration(int(duration))
        self.window.bg_padding_anim.setStartValue(self.window.bg.ring_padding)
        self.window.bg_padding_anim.setEndValue(1.0)
        self.window.bg_padding_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.window.bg_padding_anim.start()

        if hasattr(self.window, "sound_manager"):
            self.window.sound_manager.breath_exhale(int(duration))

    def on_hold_start(self, duration, color):
        if self.window.text_color_anim and self.window.text_color_anim.state() != QAbstractAnimation.Stopped:
            self.window.text_color_anim.stop()
        self.window.text_color_anim = QVariantAnimation(self.window)
        self.window.text_color_anim.setDuration(int(duration))
        self.window.text_color_anim.setStartValue(self.window.current_text_color)
        self.window.text_color_anim.setEndValue(color)
        self.window.text_color_anim.valueChanged.connect(self.window._update_label_color)
        self.window.text_color_anim.start()

    def on_breath_end(self, duration, inhale, exhale):
        self.window.last_cycle_duration = duration
        self.window.last_inhale = inhale
        self.window.last_exhale = exhale
        self.window.cycle_durations.append({"inhale": inhale, "exhale": exhale})
        self.window.stats_overlay.update_minutes(self.window.meditation_seconds)

    def end_session(self):
        if not self.window.session_active:
            return
        self.window.session_active = False
        start_str = self.window.session_start.strftime("%H:%M:%S") if self.window.session_start else ""
        duration_seconds = self.window.session_seconds
        breaths = self.window.circle.breath_count
        new_badges = self.window.data_store.add_session(
            self.window.session_start,
            duration_seconds,
            breaths,
            self.window.last_inhale,
            self.window.last_exhale,
            self.window.cycle_durations,
        )
        self.window.stats_overlay.update_last_session(
            start_str,
            duration_seconds,
            breaths,
            self.window.last_inhale,
            self.window.last_exhale,
            self.window.cycle_durations,
        )
        self.window.stats_overlay.update_minutes(self.window.meditation_seconds)

        end_time_str = self.window.data_store.now().strftime("%I:%M %p")
        start_time_str = self.window.session_start.strftime("%I:%M %p")
        self.window.session_complete.set_stats(
            duration_seconds,
            breaths,
            self.window.last_inhale,
            self.window.last_exhale,
            start_time_str,
            end_time_str,
        )
        if new_badges:
            self.window.session_complete.show_badges(new_badges)
        else:
            self.window.session_complete.show_badges([])
        self.window.stats_overlay.update_streak(self.window.data_store.get_streak())
        self.window.stats_overlay.update_badges(
            self.window.data_store.get_badges_for_date(self.window.data_store.now())
        )
        self.window.menu_handler.hide_control_buttons()
        self.window.dev_menu.hide()

        if hasattr(self.window, "bg_anim") and self.window.bg_anim.state() != QAbstractAnimation.Stopped:
            self.window.bg_anim.stop()
        self.window.bg_anim = QPropertyAnimation(self.window.bg, b"opacity", self.window)
        self.window.bg_anim.setDuration(1000)
        self.window.bg_anim.setStartValue(self.window.bg.opacity)
        self.window.bg_anim.setEndValue(0.0)
        self.window.bg_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.window.bg_anim.start()

        self.window.show_biofeedback_message()

    def toggle_developer_speed(self):
        self.window.speed_multiplier = 10 if getattr(self.window, "speed_multiplier", 1) == 1 else 1
        self.update_speed()
        if self.window.speed_multiplier == 1:
            self.window.data_store.reset_offset()
        txt = "Modo desarrollador ON" if self.window.speed_multiplier > 1 else "Modo desarrollador OFF"
        self.window.display_motivational_message(txt)

    def advance_day(self):
        self.window.data_store.advance_day()
        self.window.meditation_seconds = self.window.data_store.get_today_seconds()
        self.window.stats_overlay.update_minutes(self.window.meditation_seconds)
        self.window.stats_overlay.update_badges(
            self.window.data_store.get_badges_for_date(self.window.data_store.now())
        )

    def update_speed(self):
        self.window.circle.speed_multiplier = self.window.speed_multiplier
        self.window.timer.setInterval(int(1000 / self.window.speed_multiplier))
