import json
from pathlib import Path
from datetime import datetime, timedelta
from platformdirs import user_data_dir


class DataStore:
    def __init__(self, path: str | Path | None = None):
        """Initialize the data store using a writable user data directory."""
        if path is None:
            data_dir = Path(user_data_dir("Calmio"))
            data_dir.mkdir(parents=True, exist_ok=True)
            path = data_dir / "calmio_data.json"
        self.path = Path(path)
        self.data = {
            "daily_seconds": {},
            "last_session": {},
            "streak": 1,
            "sessions": [],
            # store cumulative counts for each badge code
            "badges": {},
            # badges earned today {date: {code: count}}
            "daily_badges": {},
            "sound_settings": {
                "music_enabled": False,
                "bell_enabled": False,
                "music_mode": "scale",
                "scale_type": "major",
            },
        }
        self.time_offset = timedelta()
        self.load()

    def now(self):
        """Return the current datetime adjusted by any developer offset."""
        return datetime.now() + self.time_offset

    def advance_day(self, days: int = 1):
        """Shift the virtual clock forward by the given number of days."""
        self.time_offset += timedelta(days=days)

    def reset_offset(self):
        """Clear any developer time offset."""
        self.time_offset = timedelta()

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
                    if "badges" not in self.data:
                        self.data["badges"] = {}
                    elif isinstance(self.data["badges"], list):
                        self.data["badges"] = {b: 1 for b in self.data["badges"]}
                    if "daily_badges" not in self.data:
                        self.data["daily_badges"] = {}
                    else:
                        # convert old format lists to count dicts
                        for k, v in list(self.data["daily_badges"].items()):
                            if isinstance(v, list):
                                counts = {}
                                for b in v:
                                    counts[b] = counts.get(b, 0) + 1
                                self.data["daily_badges"][k] = counts
                    if "sound_settings" not in self.data:
                        self.data["sound_settings"] = {
                            "music_enabled": False,
                            "bell_enabled": False,
                            "music_mode": "scale",
                            "scale_type": "major",
                        }
                    else:
                        self.data["sound_settings"].setdefault("music_mode", "scale")
                        self.data["sound_settings"].setdefault("scale_type", "major")
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # ------------------------------------------------------------------
    def get_sound_setting(self, name: str, default=None):
        return self.data.get("sound_settings", {}).get(name, default)

    def set_sound_setting(self, name: str, value) -> None:
        self.data.setdefault("sound_settings", {})[name] = value
        self.save()

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
        new_badges = self._check_badges(start_dt, seconds, breaths)
        daily_only = {
            "1_session_day",
            "2_sessions_day",
            "3_sessions_day",
            "3_day_streak",
            "7_day_streak",
            "30_day_streak",
        }
        session_badges = [b for b in new_badges if b not in daily_only]
        # store only session-related badges with the session
        self.data["sessions"][-1]["badges"] = list(session_badges)
        if new_badges:
            day_badges = self.data.setdefault("daily_badges", {}).get(date_key, {})
            for b in new_badges:
                day_badges[b] = day_badges.get(b, 0) + 1
                self.data["badges"][b] = self.data["badges"].get(b, 0) + 1
            self.data["daily_badges"][date_key] = day_badges
        self.save()
        return session_badges

    def get_today_seconds(self):
        today_key = self.now().date().isoformat()
        return self.data["daily_seconds"].get(today_key, 0)

    def get_last_session(self):
        return self.data.get("last_session", {})

    def get_badges(self):
        return self.data.get("badges", {})

    def get_badges_for_date(self, date_obj):
        date_key = (
            date_obj.date().isoformat() if hasattr(date_obj, "date") else date_obj.isoformat()
        )
        return self.data.get("daily_badges", {}).get(date_key, {})

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

    def _check_badges(self, start_dt, session_seconds, breaths):
        """Check and award badges based on totals, session data and streak."""
        new_badges = []

        # total meditation time badges
        total_minutes = sum(self.data["daily_seconds"].values()) / 60
        if total_minutes >= 5 and "5_min_total" not in self.data["badges"]:
            new_badges.append("5_min_total")

        # breaths per session badges
        breath_levels = [
            (1, "1_breath_session"),
            (5, "5_breaths_session"),
            (10, "10_breaths"),
            (20, "20_breaths_session"),
            (30, "30_breaths_session"),
            (40, "40_breaths_session"),
            (50, "50_breaths_session"),
            (60, "60_breaths_session"),
            (80, "80_breaths_session"),
            (100, "100_breaths_session"),
        ]
        for count, code in breath_levels:
            if breaths >= count:
                new_badges.append(code)

        # number of sessions in a day badges
        date_key = start_dt.date().isoformat()
        sessions_today = len(
            [s for s in self.data.get("sessions", []) if s.get("start", "").startswith(date_key)]
        )
        session_levels = [
            (1, "1_session_day"),
            (2, "2_sessions_day"),
            (3, "3_sessions_day"),
        ]
        for count, code in session_levels:
            if sessions_today >= count:
                new_badges.append(code)

        # streak based badges
        if self.data.get("streak", 1) >= 3 and "3_day_streak" not in self.data["badges"]:
            new_badges.append("3_day_streak")
        if self.data.get("streak", 1) >= 7 and "7_day_streak" not in self.data["badges"]:
            new_badges.append("7_day_streak")
        if self.data.get("streak", 1) >= 30 and "30_day_streak" not in self.data["badges"]:
            new_badges.append("30_day_streak")

        return new_badges

    def get_weekly_summary(self, reference_date=None):
        """Return stats for the week of the given date (default today)."""
        if reference_date is None:
            reference_date = self.now().date()
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
            "minutes_per_day": minutes_per_day,
            "total": total_seconds / 60,
            "average": average,
            "longest_day": longest_day,
            "longest_time": longest_time,
            "longest_minutes": longest_secs / 60,
            "total_seconds": total_seconds,
        }

    def get_monthly_summary(self, year, month, goal=600):
        """Return stats for the specified month."""
        from datetime import date

        start = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        days = (next_month - start).days

        # minutes per week (fixed day ranges: 1-7, 8-14, 15-21, 22-end)
        weeks = []
        for start_day in (1, 8, 15, 22):
            day_start = start + timedelta(days=start_day - 1)
            if day_start >= next_month:
                break
            day_end = min(start_day + 6, days)
            total = 0
            for i in range(start_day, day_end + 1):
                d = start + timedelta(days=i - 1)
                total += self.data["daily_seconds"].get(d.isoformat(), 0)
            weeks.append(total / 60)

        total_minutes = sum(weeks)
        average = total_minutes / days if days else 0
        best_week_idx = 1 + weeks.index(max(weeks)) if weeks else 0

        # longest streak in month
        longest = 0
        current_streak = 0
        for i in range(days):
            day = start + timedelta(days=i)
            if self.data["daily_seconds"].get(day.isoformat(), 0) > 0:
                current_streak += 1
                longest = max(longest, current_streak)
            else:
                current_streak = 0

        return {
            "minutes_per_week": [int(round(m)) for m in weeks],
            "total": total_minutes,
            "average": average,
            "best_week": best_week_idx,
            "longest_streak": longest,
            "goal": goal,
        }

    def clear_data(self):
        """Delete stored data and reset to defaults."""
        if self.path.exists():
            try:
                self.path.unlink()
            except OSError:
                pass
        self.data = {
            "daily_seconds": {},
            "last_session": {},
            "streak": 1,
            "sessions": [],
            "badges": {},
            "daily_badges": {},
            "sound_settings": {
                "music_enabled": False,
                "bell_enabled": False,
                "music_mode": "scale",
                "scale_type": "major",
            },
        }
        self.save()
