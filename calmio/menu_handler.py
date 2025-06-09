from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


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
        self.window.stats_overlay.setGeometry(self.window.rect())
        self.window.today_sessions.setGeometry(self.window.rect())
        self.window.session_details.setGeometry(self.window.rect())
        if hasattr(self.window, "options_overlay"):
            self.window.options_overlay.setGeometry(self.window.rect())
        if hasattr(self.window, "sound_overlay"):
            self.window.sound_overlay.setGeometry(self.window.rect())
        if hasattr(self.window, "breath_modes"):
            self.window.breath_modes.setGeometry(self.window.rect())

    def _setup_control_button(self, button: QPushButton) -> None:
        """Apply common styling to control buttons."""
        button.setFixedSize(40, 40)
        button.setStyleSheet("QPushButton {background:none; border:none; font-size:20px;}")
        button.setFocusPolicy(Qt.NoFocus)
        button.hide()

    # --- visibility toggles --------------------------------------------
    def toggle_menu(self) -> None:
        """Show or hide the glass style main menu."""
        if self.window.main_menu_overlay.isVisible():
            self.close_main_menu()
        else:
            self.window.main_menu_overlay.open()

    def close_main_menu(self) -> None:
        self.window.main_menu_overlay.close()

    def toggle_options(self) -> None:
        if self.window.options_overlay.isVisible():
            self.close_options()
        else:
            self.window.options_overlay.show()
            self.window.options_overlay.raise_()

    def close_options(self) -> None:
        self.window.options_overlay.hide()
        self.hide_control_buttons()

    def toggle_developer_menu(self) -> None:
        pass

    def toggle_sound(self) -> None:
        if self.window.sound_overlay.isVisible():
            self.close_sound()
        else:
            self.window.sound_overlay.show()
            self.window.sound_overlay.raise_()

    def close_sound(self) -> None:
        self.window.sound_overlay.hide()
        self.hide_control_buttons()

    def toggle_breath_modes(self) -> None:
        if self.window.breath_modes.isVisible():
            self.close_breath_modes()
        else:
            self.window.breath_modes.show()
            self.window.breath_modes.raise_()

    def close_breath_modes(self) -> None:
        self.window.breath_modes.hide()
        self.hide_control_buttons()

    def toggle_mantras(self) -> None:
        if self.window.mantras_overlay.isVisible():
            self.close_mantras()
        else:
            self.window.mantras_overlay.show()
            self.window.mantras_overlay.raise_()

    def close_mantras(self) -> None:
        self.window.mantras_overlay.hide()


    def hide_control_buttons(self) -> None:
        for btn in self.window.control_buttons:
            btn.hide()

    def show_control_buttons(self) -> None:
        for btn in self.window.control_buttons:
            btn.show()
