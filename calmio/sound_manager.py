from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class SoundManager(QObject):
    """Manage background sounds and notifications."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        base = Path(__file__).resolve().parents[1] / "assets" / "sounds"
        self._players: dict[str, QMediaPlayer] = {}
        self._outputs: dict[str, QAudioOutput] = {}
        self.general_volume = 50
        self.music_volume = 50
        self.drop_volume = 50
        self.bell_volume = 50
        self.bell_enabled = False
        self.music_enabled = False
        self.current_env: str | None = None
        self._bell_fade_timer: QTimer | None = None
        self._bell_fade_start: float = 0.0
        self._fade_timer: QTimer | None = None  # legacy, kept for compatibility
        self._fade_start: float = 0.0
        self.note_index = 0
        sound_files = {
            "bosque": "bosque.mp3",
            "lluvia": "LLUVIA.mp3",
            "fuego": "fuego.mp3",
            "mar": "mar.mp3",
            "bell": "bell.mp3",
            "notado": "notado.mp3",
            "drop": "drop.mp3",
        }
        for key, filename in sound_files.items():
            player = QMediaPlayer(self)
            output = QAudioOutput(self)
            if key == "bell":
                output.setVolume(self.bell_volume / 100)
            elif key == "notado":
                output.setVolume(self.music_volume / 100)
            elif key == "drop":
                output.setVolume(self.drop_volume / 100)
            else:
                output.setVolume(self.general_volume / 100)
            player.setAudioOutput(output)
            player.setSource(QUrl.fromLocalFile(str(base / filename)))
            loops = QMediaPlayer.Infinite if hasattr(QMediaPlayer, "Infinite") else -1
            if key in {"bell", "notado", "drop"}:
                player.setLoops(1)
            else:
                player.setLoops(loops)
            self._players[key] = player
            self._outputs[key] = output

    # ------------------------------------------------------------------
    def set_environment(self, name: str | None) -> None:
        """Start the given ambient loop and stop previous one."""
        if name == "none":
            name = None
        if self.current_env and self.current_env in self._players:
            self._players[self.current_env].stop()
        self.current_env = name
        if name and name in self._players:
            p = self._players[name]
            p.setPosition(0)
            self._outputs[name].setVolume(self.general_volume / 100)
            p.play()

    def set_volume(self, value: int) -> None:
        self.general_volume = value
        for k, out in self._outputs.items():
            if k not in {"bell", "notado", "drop"}:
                out.setVolume(value / 100)

    def set_music_volume(self, value: int) -> None:
        self.music_volume = value
        self._outputs["notado"].setVolume(value / 100)

    def set_drop_volume(self, value: int) -> None:
        self.drop_volume = value
        self._outputs["drop"].setVolume(value / 100)

    def set_bell_volume(self, value: int) -> None:
        self.bell_volume = value
        self._outputs["bell"].setVolume(value / 100)

    def set_bell_enabled(self, enabled: bool) -> None:
        self.bell_enabled = enabled

    def set_music_enabled(self, enabled: bool) -> None:
        if self.music_enabled == enabled:
            return
        self.music_enabled = enabled
        if not enabled:
            player = self._players["notado"]
            player.stop()
        self.note_index = 0

    def maybe_play_bell(self, count: int) -> None:
        if self.bell_enabled and count % 10 == 0:
            bell = self._players["bell"]
            bell.stop()
            bell.setPosition(0)
            self._outputs["bell"].setVolume(self.bell_volume / 100)
            bell.play()
            self._bell_fade_start = time.monotonic()
            if self._bell_fade_timer is None:
                self._bell_fade_timer = QTimer(self)
                self._bell_fade_timer.timeout.connect(self._update_bell_fade)
            self._bell_fade_timer.start(100)

    def _update_bell_fade(self) -> None:
        duration = 3.0
        elapsed = time.monotonic() - self._bell_fade_start
        if elapsed >= duration:
            self._outputs["bell"].setVolume(0.0)
            if self._bell_fade_timer:
                self._bell_fade_timer.stop()
            return
        volume = (1 - elapsed / duration) * (self.bell_volume / 100)
        self._outputs["bell"].setVolume(volume)

    def maybe_play_music(self, count: int) -> None:
        if not self.music_enabled:
            return
        ratios = [
            1.0,
            1.122,
            1.26,
            1.335,
            1.498,
            1.682,
            1.887,
            2.0,
        ]
        player = self._players["notado"]
        player.stop()
        player.setPlaybackRate(ratios[self.note_index])
        player.setPosition(0)
        self._outputs["notado"].setVolume(self.music_volume / 100)
        player.play()
        self.note_index = (self.note_index + 1) % len(ratios)

    def play_drop(self) -> None:
        drop = self._players["drop"]
        drop.stop()
        drop.setPosition(0)
        self._outputs["drop"].setVolume(self.drop_volume / 100)
        drop.play()

    def mute_all(self) -> None:
        for p in self._players.values():
            p.stop()
        self.current_env = None
        self.music_enabled = False

