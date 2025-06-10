import os
import sys
from pathlib import Path
import platformdirs
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from calmio.main_window import MainWindow


def test_daily_challenge_overlay_visibility(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setattr(platformdirs, "user_data_dir", lambda *a, **k: str(tmp_path))
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    overlay = window.daily_challenge_overlay
    assert overlay is not None
    # Overlay should start hidden
    assert not overlay.isVisible()
    window.overlay_manager.show_daily_challenge()
    app.processEvents()
    assert overlay.isVisible()
    window.overlay_manager.close_daily_challenge()
    assert not overlay.isVisible()
    app.quit()
