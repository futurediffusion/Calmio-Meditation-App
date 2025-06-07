import json
from pathlib import Path
from datetime import datetime


class DataStore:
    def __init__(self, path="calmio_data.json"):
        self.path = Path(path)
        self.data = {"daily_seconds": {}, "last_session": {}}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
                    if "daily_minutes" in self.data:
                        self.data["daily_seconds"] = {
                            k: v * 60 for k, v in self.data.pop("daily_minutes").items()
                        }
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add_session(self, start_dt, seconds, breaths, inhale, exhale):
        date_key = start_dt.date().isoformat()
        self.data["daily_seconds"][date_key] = (
            self.data["daily_seconds"].get(date_key, 0) + seconds
        )
        self.data["last_session"] = {
            "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": seconds,
            "breaths": breaths,
            "last_inhale": inhale,
            "last_exhale": exhale,
        }
        self.save()

    def get_today_seconds(self):
        today_key = datetime.now().date().isoformat()
        return self.data["daily_seconds"].get(today_key, 0)

    def get_last_session(self):
        return self.data.get("last_session", {})
