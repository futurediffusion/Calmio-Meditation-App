from PySide6.QtCore import Qt


class MenuHandler:
    """Utility class to handle control button positioning and visibility."""

    def __init__(self, window):
        self.window = window

    # --- layout helpers -------------------------------------------------
    def position_buttons(self) -> None:
        """Position control buttons relative to the window size."""
        margin = 10
        x = self.window.width() - self.window.menu_button.width() - margin
        y = self.window.height() - self.window.menu_button.height() - margin
        self.window.menu_button.move(x, y)
        if hasattr(self.window, "dev_menu"):
            self.window.dev_menu.move(
                x - self.window.dev_menu.width() + self.window.menu_button.width(),
                y - self.window.dev_menu.height() - margin,
            )
        if hasattr(self.window, "menu_overlay"):
            self.window.menu_overlay.adjust_position()
        self.window.stats_overlay.setGeometry(self.window.rect())
        self.window.today_sessions.setGeometry(self.window.rect())
        self.window.session_details.setGeometry(self.window.rect())
        if hasattr(self.window, "options_overlay"):
            self.window.options_overlay.setGeometry(self.window.rect())
        if hasattr(self.window, "sound_overlay"):
            self.window.sound_overlay.setGeometry(self.window.rect())
        if hasattr(self.window, "breath_modes"):
            self.window.breath_modes.setGeometry(self.window.rect())
        if hasattr(self.window, "daily_challenge_prompt"):
            # Position the daily challenge prompt in the bottom-right corner
            px = (
                self.window.width()
                - self.window.daily_challenge_prompt.width()
                - margin
            )
            py = (
                self.window.height()
                - self.window.daily_challenge_prompt.height()
                - margin
            )
            self.window.daily_challenge_prompt.move(px, py)


    # --- visibility toggles --------------------------------------------
    def toggle_menu(self) -> None:
        if self.window.menu_overlay.isVisible():
            self.window.menu_overlay.hide_with_anim()
            self.window.dev_menu.hide()
        else:
            self.window.menu_overlay.show_with_anim()

    def toggle_options(self) -> None:
        if self.window.options_overlay.isVisible():
            self.close_options()
        else:
            self.window.options_overlay.show()
            self.window.options_overlay.raise_()
            self.window.menu_overlay.hide()

    def close_options(self) -> None:
        self.window.options_overlay.hide()
        self.window.menu_overlay.hide()
        # Restore focus to main window for breathing controls
        self.window.setFocus()

    def toggle_developer_menu(self) -> None:
        if self.window.dev_menu.isVisible():
            self.window.dev_menu.hide()
        else:
            self.window.dev_menu.show()
            self.window.dev_menu.raise_()
        self.window.menu_overlay.hide()

    def toggle_sound(self) -> None:
        if self.window.sound_overlay.isVisible():
            self.close_sound()
        else:
            self.window.sound_overlay.show()
            self.window.sound_overlay.raise_()
            self.window.menu_overlay.hide()

    def close_sound(self) -> None:
        self.window.sound_overlay.hide()
        self.window.menu_overlay.hide()
        self.window.setFocus()

    def toggle_breath_modes(self) -> None:
        if self.window.breath_modes.isVisible():
            self.close_breath_modes()
        else:
            self.window.breath_modes.show()
            self.window.breath_modes.raise_()
            self.window.menu_overlay.hide()

    def close_breath_modes(self) -> None:
        self.window.breath_modes.hide()
        self.window.menu_overlay.hide()
        self.window.setFocus()

    def hide_control_buttons(self) -> None:
        if hasattr(self.window, "menu_overlay"):
            self.window.menu_overlay.hide()
        # Ensure breathing controls receive key events again
        self.window.setFocus()

