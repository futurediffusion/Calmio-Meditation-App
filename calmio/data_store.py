import json
from pathlib import Path
from datetime import datetime


class DataStore:
    def __init__(self, path="calmio_data.json"):
        self.path = Path(path)
        self.data = {"daily_minutes": {}, "last_session": {}}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add_session(self, start_dt, minutes, breaths, last_cycle):
        date_key = start_dt.date().isoformat()
        self.data["daily_minutes"][date_key] = (
            self.data["daily_minutes"].get(date_key, 0) + minutes
        )
        self.data["last_session"] = {
            "start": start_dt.strftime("%Y-%m-%d %H:%M"),
            "minutes": minutes,
            "breaths": breaths,
            "last_cycle": last_cycle,
        }
        self.save()

    def get_today_minutes(self):
        today_key = datetime.now().date().isoformat()
        return self.data["daily_minutes"].get(today_key, 0)

    def get_last_session(self):
        return self.data.get("last_session", {})
