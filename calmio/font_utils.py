from PySide6.QtGui import QFont, QFontDatabase


def get_emoji_font(size: int = 12) -> QFont:
    """Return a font that supports color emoji if available."""
    preferred = ["Noto Color Emoji", "Segoe UI Emoji", "Apple Color Emoji"]
    families = set(QFontDatabase().families())
    for fam in preferred:
        if fam in families:
            return QFont(fam, point_size=size)
    return QFont("Sans Serif", point_size=size)
