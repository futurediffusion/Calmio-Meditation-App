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
            "badges": [],
            "daily_badges": {},
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
                    if "badges" not in self.data:
                        self.data["badges"] = []
                    if "daily_badges" not in self.data:
                        self.data["daily_badges"] = {}
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
        new_badges = self._check_badges(start_dt, seconds, breaths)
        # store badges with session
        self.data["sessions"][-1]["badges"] = list(new_badges)
        if new_badges:
            day_badges = self.data.setdefault("daily_badges", {}).get(date_key, [])
            for b in new_badges:
                if b not in day_badges:
                    day_badges.append(b)
            self.data["daily_badges"][date_key] = day_badges
        self.save()
        return new_badges

    def get_today_seconds(self):
        today_key = datetime.now().date().isoformat()
        return self.data["daily_seconds"].get(today_key, 0)

    def get_last_session(self):
        return self.data.get("last_session", {})

    def get_badges(self):
        return self.data.get("badges", [])

    def get_badges_for_date(self, date_obj):
        date_key = date_obj.date().isoformat() if hasattr(date_obj, "date") else date_obj.isoformat()
        return self.data.get("daily_badges", {}).get(date_key, [])

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
            self.data["badges"].append("5_min_total")
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
            if breaths >= count and code not in self.data["badges"]:
                self.data["badges"].append(code)
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
            if sessions_today >= count and code not in self.data["badges"]:
                self.data["badges"].append(code)
                new_badges.append(code)

        # streak based badges
        if self.data.get("streak", 1) >= 3 and "3_day_streak" not in self.data["badges"]:
            self.data["badges"].append("3_day_streak")
            new_badges.append("3_day_streak")
        if self.data.get("streak", 1) >= 7 and "7_day_streak" not in self.data["badges"]:
            self.data["badges"].append("7_day_streak")
            new_badges.append("7_day_streak")
        if self.data.get("streak", 1) >= 30 and "30_day_streak" not in self.data["badges"]:
            self.data["badges"].append("30_day_streak")
            new_badges.append("30_day_streak")

        return new_badges

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

    def get_monthly_summary(self, year, month, goal=600):
        """Return stats for the specified month."""
        from datetime import date

        start = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        days = (next_month - start).days

        # minutes per week
        weeks = []
        current = start
        while current < next_month:
            week_end = current + timedelta(days=6 - current.weekday())
            if week_end >= next_month:
                week_end = next_month - timedelta(days=1)
            total = 0
            d = current
            while d <= week_end:
                total += self.data["daily_seconds"].get(d.isoformat(), 0)
                d += timedelta(days=1)
            weeks.append(total / 60)
            current = week_end + timedelta(days=1)

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
