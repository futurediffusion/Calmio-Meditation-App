import json
from pathlib import Path
from datetime import datetime, timedelta


class DataStore:
    def __init__(self, path="calmio_data.json"):
        self.path = Path(path)
        self.data = {
            "daily_seconds": {},
            "last_session": {},
            "streak": 1,
            "sessions": [],
        }
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
                    if "streak" not in self.data:
                        self.data["streak"] = 1
                    if "sessions" not in self.data:
                        self.data["sessions"] = []
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add_session(self, start_dt, seconds, breaths, inhale, exhale, cycles=None):
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
            "cycles": cycles or [],
        }
        self._update_streak()
        self.data.setdefault("sessions", []).append(
            {
                "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": seconds,
                "breaths": breaths,
                "last_inhale": inhale,
                "last_exhale": exhale,
                "cycles": cycles or [],
            }
        )
        self.save()

    def get_today_seconds(self):
        today_key = datetime.now().date().isoformat()
        return self.data["daily_seconds"].get(today_key, 0)

    def get_last_session(self):
        return self.data.get("last_session", {})

    def get_sessions_for_date(self, date_obj):
        date_key = date_obj.date().isoformat() if hasattr(date_obj, "date") else date_obj.isoformat()
        sessions = []
        for s in self.data.get("sessions", []):
            try:
                dt = datetime.fromisoformat(s.get("start", ""))
            except ValueError:
                continue
            if dt.date().isoformat() == date_key:
                sessions.append(s)
        sessions.sort(key=lambda x: x.get("start", ""), reverse=True)
        return sessions

    def get_streak(self):
        return self.data.get("streak", 1)

    def _update_streak(self):
        dates = sorted(self.data["daily_seconds"].keys())
        if not dates:
            self.data["streak"] = 0
            return
        streak = 1
        prev = datetime.fromisoformat(dates[-1]).date()
        for d in reversed(dates[:-1]):
            current = datetime.fromisoformat(d).date()
            if (prev - current).days == 1:
                streak += 1
                prev = current
            else:
                break
        self.data["streak"] = streak

    def get_weekly_summary(self, reference_date=None):
        """Return stats for the week of the given date (default today)."""
        if reference_date is None:
            reference_date = datetime.now().date()
        start = reference_date - timedelta(days=reference_date.weekday())
        minutes_per_day = []
        total_seconds = 0
        for i in range(7):
            d = start + timedelta(days=i)
            secs = self.data["daily_seconds"].get(d.isoformat(), 0)
            minutes_per_day.append(secs / 60)
            total_seconds += secs

        longest_secs = 0
        longest_day = ""
        longest_time = ""
        for s in self.data.get("sessions", []):
            try:
                dt = datetime.fromisoformat(s.get("start", ""))
            except ValueError:
                continue
            if start <= dt.date() <= start + timedelta(days=6):
                dur = s.get("duration", 0)
                if dur > longest_secs:
                    longest_secs = dur
                    eng_day = dt.strftime("%A")
                    day_map = {
                        "Monday": "Lunes",
                        "Tuesday": "Martes",
                        "Wednesday": "Mi\u00e9rcoles",
                        "Thursday": "Jueves",
                        "Friday": "Viernes",
                        "Saturday": "S\u00e1bado",
                        "Sunday": "Domingo",
                    }
                    longest_day = day_map.get(eng_day, eng_day)
                    longest_time = dt.strftime("%H:%M")

        average = (total_seconds / 60) / 7 if total_seconds else 0
        return {
            "minutes_per_day": [int(round(m)) for m in minutes_per_day],
            "total": total_seconds / 60,
            "average": average,
            "longest_day": longest_day,
            "longest_time": longest_time,
            "longest_minutes": longest_secs / 60,
        }
