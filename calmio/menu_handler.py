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
        self.window.options_button.move(x - self.window.options_button.width() - margin, y)
        self.window.stats_button.move(x - 2 * (self.window.menu_button.width() + margin), y)
        self.window.end_button.move(x - 3 * (self.window.menu_button.width() + margin), y)
        self.window.dev_button.move(x - 4 * (self.window.menu_button.width() + margin), y)
        if hasattr(self.window, "dev_menu"):
            self.window.dev_menu.move(
                self.window.dev_button.x() - self.window.dev_menu.width() + self.window.dev_button.width(),
                self.window.dev_button.y() - self.window.dev_menu.height() - margin,
            )
        self.window.stats_overlay.setGeometry(self.window.rect())
        self.window.today_sessions.setGeometry(self.window.rect())
        self.window.session_details.setGeometry(self.window.rect())
        if hasattr(self.window, "options_overlay"):
            self.window.options_overlay.setGeometry(self.window.rect())

    def _setup_control_button(self, button: QPushButton) -> None:
        """Apply common styling to control buttons."""
        button.setFixedSize(40, 40)
        button.setStyleSheet("QPushButton {background:none; border:none; font-size:20px;}")
        button.setFocusPolicy(Qt.NoFocus)
        button.hide()

    # --- visibility toggles --------------------------------------------
    def toggle_menu(self) -> None:
        if self.window.options_button.isVisible():
            self.hide_control_buttons()
            self.window.dev_menu.hide()
        else:
            self.show_control_buttons()

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
        if self.window.dev_menu.isVisible():
            self.window.dev_menu.hide()
        else:
            self.window.dev_menu.show()
            self.window.dev_menu.raise_()

    def hide_control_buttons(self) -> None:
        for btn in self.window.control_buttons:
            btn.hide()

    def show_control_buttons(self) -> None:
        for btn in self.window.control_buttons:
            btn.show()
