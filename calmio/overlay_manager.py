class OverlayManager:
    """Handle opening and closing of secondary views and overlays."""

    def __init__(self, window):
        self.window = window

    # ------------------------------------------------------------------
    def toggle_stats(self):
        if self.window.stats_overlay.isVisible():
            self.window.stats_overlay.hide()
            self.window.today_sessions.hide()
            self.window.session_details.hide()
        else:
            self.window.today_sessions.hide()
            self.window.session_details.hide()
            self.window.stats_overlay.show()
            self.window.stats_overlay.raise_()

    def close_stats(self):
        self.window.stats_overlay.hide()
        self.window.menu_handler.hide_control_buttons()

    def open_today_sessions(self):
        sessions = self.window.data_store.get_sessions_for_date(self.window.data_store.now())
        self.window.today_sessions.set_sessions(sessions)
        self.window.stats_overlay.hide()
        self.window.session_details.hide()
        self.window.today_sessions.show()
        self.window.today_sessions.raise_()

    def close_today_sessions(self):
        self.window.today_sessions.hide()
        self.window.stats_overlay.show()
        self.window.stats_overlay.raise_()

    def on_session_complete_done(self):
        self.window.stack.setCurrentWidget(self.window.main_view)
        self.window.stats_overlay.show_tab(0)
        self.window.stats_overlay.show()
        self.window.stats_overlay.raise_()
        self.window.circle.breath_count = 0
        self.window.label.setText("")
        self.window.count_opacity.setOpacity(0)
        self.window.session_seconds = 0
        self.window.menu_handler.hide_control_buttons()
        self.window.start_prompt_animation()

    def on_session_complete_closed(self):
        self.window.stack.setCurrentWidget(self.window.main_view)
        self.window.circle.breath_count = 0
        self.window.label.setText("")
        self.window.count_opacity.setOpacity(0)
        self.window.session_seconds = 0
        self.window.menu_handler.hide_control_buttons()
        self.window.start_prompt_animation()

    def open_session_details(self, session):
        is_last = False
        try:
            is_last = session == self.window.data_store.get_last_session()
        except Exception:
            pass
        self.window.session_details.set_session(session, is_last=is_last)
        self.window.stats_overlay.hide()
        self.window.today_sessions.hide()
        self.window.session_details.show()
        self.window.session_details.raise_()

    def close_session_details(self):
        self.window.session_details.hide()
        self.window.stats_overlay.show()
        self.window.stats_overlay.raise_()

    def open_today_badges(self):
        badges = self.window.data_store.get_badges_for_date(self.window.data_store.now())
        self.window.badges_view.title_lbl.setText("Logros de hoy")
        self.window.badges_view.set_badges(badges)
        self.window._badges_return = self.window.stats_overlay
        self.window.stats_overlay.hide()
        self.window.badges_view.show()
        self.window.badges_view.raise_()

    def open_session_badges(self, badges, return_to=None):
        self.window.badges_view.title_lbl.setText("Logros de sesión")
        self.window.badges_view.set_badges(badges)
        if return_to is None:
            return_to = self.window.session_details
        self.window._badges_return = return_to
        return_to.hide()
        self.window.badges_view.show()
        self.window.badges_view.raise_()

    def close_badges_view(self):
        self.window.badges_view.hide()
        if self.window._badges_return:
            self.window._badges_return.show()
            self.window._badges_return.raise_()

    # ------------------------------------------------------------------
    def show_daily_challenge(self):
        if not hasattr(self.window, "daily_challenge_overlay"):
            return
        self.window.daily_challenge_overlay.setGeometry(self.window.rect())
        self.window.daily_challenge_overlay.show()
        self.window.daily_challenge_overlay.raise_()

    def close_daily_challenge(self):
        if hasattr(self.window, "daily_challenge_overlay"):
            self.window.daily_challenge_overlay.hide()
        if hasattr(self.window, "hide_daily_challenge_prompt"):
            self.window.hide_daily_challenge_prompt()
