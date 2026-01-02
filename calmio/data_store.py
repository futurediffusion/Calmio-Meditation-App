import json
from pathlib import Path
from datetime import datetime, timedelta, date
from peewee import fn, DoesNotExist

from .database import (
    initialize_database,
    Setting,
    Session,
    Badge,
    DailyBadge,
    DailyChallenge,
    db,
)


from platformdirs import user_data_dir


class DataStore:
    def __init__(self, path: str | Path | None = None):
        """Initialize the data store using a writable user data directory."""
        self.time_offset = timedelta()
        self.db_path = path or Path(user_data_dir("Calmio")) / "calmio.db"
        initialize_database()
        self._migrate_from_json()

    def _migrate_from_json(self):
        """Migrate data from the old JSON file to the database if it exists."""
        json_path = self.db_path.parent / "calmio_data.json"
        if not json_path.exists():
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        # Check if migration has already been done
        if Setting.select().count() > 0 or Session.select().count() > 0:
            return

        with db.atomic():
            # Migrate sessions
            for session_data in data.get("sessions", []):
                try:
                    start_time = datetime.fromisoformat(session_data["start"])
                    Session.create(
                        start_time=start_time,
                        duration=session_data.get("duration", 0),
                        breaths=session_data.get("breaths", 0),
                        last_inhale=session_data.get("last_inhale", 0),
                        last_exhale=session_data.get("last_exhale", 0),
                        cycles=session_data.get("cycles", []),
                    )
                except (ValueError, KeyError):
                    continue

            # Migrate settings
            if "visual_settings" in data:
                self._set_setting("visual_settings", data["visual_settings"])
            if "sound_settings" in data:
                self._set_setting("sound_settings", data["sound_settings"])

            # Migrate badges
            for code, count in data.get("badges", {}).items():
                Badge.create(code=code, count=count)

            # Migrate daily badges
            for date_str, badges in data.get("daily_badges", {}).items():
                try:
                    date_obj = datetime.fromisoformat(date_str).date()
                    for code, count in badges.items():
                        badge, _ = Badge.get_or_create(code=code)
                        DailyBadge.create(date=date_obj, badge=badge, count=count)
                except (ValueError, KeyError):
                    continue

            # Migrate daily challenges
            for date_str, challenge_data in data.get("daily_challenges", {}).items():
                try:
                    date_obj = datetime.fromisoformat(date_str).date()
                    DailyChallenge.create(
                        date=date_obj,
                        text=challenge_data.get("text", ""),
                        completed=challenge_data.get("completed", False),
                    )
                except (ValueError, KeyError):
                    continue

        # Archive the old JSON file
        archive_path = json_path.with_suffix(".json.migrated")
        json_path.rename(archive_path)

    def now(self):
        """Return the current datetime adjusted by any developer offset."""
        return datetime.now() + self.time_offset

    def advance_day(self, days: int = 1):
        """Shift the virtual clock forward by the given number of days."""
        self.time_offset += timedelta(days=days)

    def reset_offset(self):
        """Clear any developer time offset."""
        self.time_offset = timedelta()

    def _get_setting(self, key, default=None):
        try:
            setting = Setting.get(Setting.key == key)
            return setting.value
        except DoesNotExist:
            return default if default is not None else {}

    def _set_setting(self, key, value):
        setting, created = Setting.get_or_create(key=key, defaults={"value": value})
        if not created:
            setting.value = value
            setting.save()

    # ------------------------------------------------------------------
    def get_visual_setting(self, name: str, default=None):
        settings = self._get_setting("visual_settings", {"dark_mode": False})
        return settings.get(name, default)

    def set_visual_setting(self, name: str, value) -> None:
        settings = self._get_setting("visual_settings", {"dark_mode": False})
        settings[name] = value
        self._set_setting("visual_settings", settings)

    # ------------------------------------------------------------------
    def get_sound_setting(self, name: str, default=None):
        defaults = {
            "music_enabled": False,
            "bell_enabled": False,
            "music_mode": "scale",
            "scale_type": "major",
            "breath_volume": False,
        }
        settings = self._get_setting("sound_settings", defaults)
        return settings.get(name, default)

    def set_sound_setting(self, name: str, value) -> None:
        defaults = {
            "music_enabled": False,
            "bell_enabled": False,
            "music_mode": "scale",
            "scale_type": "major",
            "breath_volume": False,
        }
        settings = self._get_setting("sound_settings", defaults)
        settings[name] = value
        self._set_setting("sound_settings", settings)

    def add_session(self, start_dt, seconds, breaths, inhale, exhale, cycles=None):
        session = Session.create(
            start_time=start_dt,
            duration=seconds,
            breaths=breaths,
            last_inhale=inhale,
            last_exhale=exhale,
            cycles=cycles or [],
        )

        new_badges = self._check_badges(start_dt, seconds, breaths)

        try:
            from .achievements import BADGE_MAP
        except ImportError:
            from achievements import BADGE_MAP

        daily_only_codes = {
            "1_session_day",
            "2_sessions_day",
            "3_sessions_day",
            "3_day_streak",
            "7_day_streak",
            "30_day_streak",
        }
        session_badges = [b for b in new_badges if b not in daily_only_codes]

        if new_badges:
            date_key = start_dt.date()
            for code in new_badges:
                badge_id = BADGE_MAP.get(code, code)
                badge, _ = Badge.get_or_create(code=badge_id)
                badge.count = (badge.count or 0) + 1
                badge.save()

                daily_badge, created = DailyBadge.get_or_create(
                    date=date_key, badge=badge
                )
                if not created:
                    daily_badge.count = (daily_badge.count or 0) + 1
                else:
                    daily_badge.count = 1
                daily_badge.save()

        return [BADGE_MAP.get(b, b) for b in session_badges]

    def get_today_seconds(self):
        today = self.now().date()
        query = Session.select(fn.SUM(Session.duration)).where(
            fn.STRFTIME("%Y-%m-%d", Session.start_time) == today.isoformat()
        )
        total_seconds = query.scalar() or 0
        return total_seconds

    def get_last_session(self):
        try:
            last = Session.select().order_by(Session.start_time.desc()).get()
            return {
                "start": last.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": last.duration,
                "breaths": last.breaths,
                "last_inhale": last.last_inhale,
                "last_exhale": last.last_exhale,
                "cycles": last.cycles or [],
            }
        except DoesNotExist:
            return {}

    def get_badges(self):
        return {b.code: b.count for b in Badge.select()}

    def get_badges_for_date(self, date_obj):
        date_key = date_obj.date() if hasattr(date_obj, "date") else date_obj
        badges = (
            Badge.select(Badge.code, DailyBadge.count)
            .join(DailyBadge)
            .where(fn.STRFTIME("%Y-%m-%d", DailyBadge.date) == date_key.isoformat())
        )
        return {b.code: b.dailybadge.count for b in badges}

    def get_sessions_for_date(self, date_obj):
        date_key = date_obj.date() if hasattr(date_obj, "date") else date_obj
        sessions_query = Session.select().where(
            fn.STRFTIME("%Y-%m-%d", Session.start_time) == date_key.isoformat()
        )
        sessions = [
            {
                "start": s.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": s.duration,
                "breaths": s.breaths,
                "last_inhale": s.last_inhale,
                "last_exhale": s.last_exhale,
                "cycles": s.cycles or [],
            }
            for s in sessions_query
        ]
        sessions.sort(key=lambda x: x.get("start", ""), reverse=True)
        return sessions

    def get_streak(self):
        dates_query = (
            Session.select(
                fn.STRFTIME("%Y-%m-%d", Session.start_time).alias("session_date")
            )
            .distinct()
            .order_by(fn.STRFTIME("%Y-%m-%d", Session.start_time).desc())
        )
        dates = [
            datetime.strptime(d.session_date, "%Y-%m-%d").date() for d in dates_query
        ]

        if not dates:
            return 0

        today = self.now().date()
        last_session_date = dates[0]

        if (today - last_session_date).days > 1:
            return 0

        streak = 1
        for i in range(len(dates) - 1):
            if (dates[i] - dates[i + 1]).days == 1:
                streak += 1
            else:
                break
        return streak

    def _check_badges(self, start_dt, session_seconds, breaths):
        """Check and award badges based on totals, session data and streak."""
        new_badges = []
        existing_badges = self.get_badges()

        total_seconds = Session.select(fn.SUM(Session.duration)).scalar() or 0
        total_minutes = total_seconds / 60
        if total_minutes >= 5 and "5_min_total" not in existing_badges:
            new_badges.append("5_min_total")

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

        date_key = start_dt.date()
        sessions_today = Session.select().where(
            fn.STRFTIME("%Y-%m-%d", Session.start_time) == date_key.isoformat()
        )
        sessions_today_count = sessions_today.count()

        session_levels = [
            (1, "1_session_day"),
            (2, "2_sessions_day"),
            (3, "3_sessions_day"),
        ]
        for count, code in session_levels:
            if sessions_today_count >= count:
                new_badges.append(code)

        streak = self.get_streak()
        if streak >= 3 and "3_day_streak" not in existing_badges:
            new_badges.append("3_day_streak")
        if streak >= 7 and "7_day_streak" not in existing_badges:
            new_badges.append("7_day_streak")
        if streak >= 30 and "30_day_streak" not in existing_badges:
            new_badges.append("30_day_streak")

        try:
            from .achievements import BADGE_MAP
        except ImportError:
            from achievements import BADGE_MAP

        return [BADGE_MAP.get(b, b) for b in new_badges]

    # ------------------------------------------------------------------
    def get_weekly_summary(self, reference_date=None):
        if reference_date is None:
            reference_date = self.now().date()
        start_of_week = reference_date - timedelta(days=reference_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        minutes_per_day = []
        total_seconds = 0
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            secs = (
                Session.select(fn.SUM(Session.duration))
                .where(fn.STRFTIME("%Y-%m-%d", Session.start_time) == day.isoformat())
                .scalar()
                or 0
            )
            minutes_per_day.append(secs / 60)
            total_seconds += secs

        longest_session = (
            Session.select()
            .where(Session.start_time.between(start_of_week, end_of_week))
            .order_by(Session.duration.desc())
            .first()
        )

        longest_day, longest_time, longest_secs = "", "", 0
        if longest_session:
            dt = longest_session.start_time
            eng_day = dt.strftime("%A")
            day_map = {
                "Monday": "Lunes",
                "Tuesday": "Martes",
                "Wednesday": "Miércoles",
                "Thursday": "Jueves",
                "Friday": "Viernes",
                "Saturday": "Sábado",
                "Sunday": "Domingo",
            }
            longest_day = day_map.get(eng_day, eng_day)
            longest_time = dt.strftime("%H:%M")
            longest_secs = longest_session.duration

        average = (total_seconds / 60) / 7 if total_seconds else 0
        return {
            "minutes_per_day": minutes_per_day,
            "total": total_seconds / 60,
            "average": average,
            "longest_day": longest_day,
            "longest_time": longest_time,
            "longest_minutes": longest_secs / 60,
        }

    def get_monthly_summary(self, year, month, goal=600):
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        days_in_month = (end_date - start_date).days
        sessions = Session.select().where(
            Session.start_time.between(start_date, end_date)
        )

        daily_seconds = {
            d.isoformat(): 0
            for d in (start_date + timedelta(days=i) for i in range(days_in_month))
        }
        for s in sessions:
            day_key = s.start_time.date().isoformat()
            daily_seconds[day_key] += s.duration

        weeks = []
        for start_day in (1, 8, 15, 22):
            day_start = start_date + timedelta(days=start_day - 1)
            if day_start >= end_date:
                break
            day_end_num = min(start_day + 6, days_in_month)
            total = 0
            for i in range(start_day, day_end_num + 1):
                d = start_date + timedelta(days=i - 1)
                total += daily_seconds.get(d.isoformat(), 0)
            weeks.append(total / 60)

        total_minutes = sum(weeks)
        average = total_minutes / days_in_month if days_in_month else 0
        best_week_idx = 1 + weeks.index(max(weeks)) if weeks else 0

        longest = 0
        current_streak = 0
        for i in range(days_in_month):
            day = start_date + timedelta(days=i)
            if daily_seconds.get(day.isoformat(), 0) > 0:
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
        """Delete all data from the database."""
        with db.atomic():
            for model in [Session, Badge, DailyBadge, DailyChallenge, Setting]:
                model.delete().execute()

    def get_challenge_for_date(self, date_obj=None):
        if date_obj is None:
            date_obj = self.now().date()
        date_key = date_obj.date() if hasattr(date_obj, "date") else date_obj
        try:
            challenge = DailyChallenge.get(
                fn.STRFTIME("%Y-%m-%d", DailyChallenge.date) == date_key.isoformat()
            )
            return {"text": challenge.text, "completed": challenge.completed}
        except DoesNotExist:
            return None

    def set_daily_challenge(self, text: str, date_obj=None):
        if date_obj is None:
            date_obj = self.now().date()
        date_key = date_obj.date() if hasattr(date_obj, "date") else date_obj
        challenge, _ = DailyChallenge.get_or_create(
            date=date_key, defaults={"text": text, "completed": False}
        )
        challenge.text = text
        challenge.save()

    def mark_challenge_completed(self, date_obj=None):
        if date_obj is None:
            date_obj = self.now().date()
        date_key = date_obj.date() if hasattr(date_obj, "date") else date_obj
        try:
            challenge = DailyChallenge.get(
                fn.STRFTIME("%Y-%m-%d", DailyChallenge.date) == date_key.isoformat()
            )
            challenge.completed = True
            challenge.save()
        except DoesNotExist:
            DailyChallenge.create(
                date=date_key, text="Reto completado", completed=True
            )

    def export_to_json(self, file_path: str):
        """Export all data to a JSON file."""
        data_export = {
            "sessions": [
                {
                    "start": s.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": s.duration,
                    "breaths": s.breaths,
                    "last_inhale": s.last_inhale,
                    "last_exhale": s.last_exhale,
                    "cycles": s.cycles,
                }
                for s in Session.select()
            ],
            "badges": {b.code: b.count for b in Badge.select()},
            "daily_badges": {},
            "daily_challenges": {
                c.date.strftime("%Y-%m-%d"): {
                    "text": c.text,
                    "completed": c.completed,
                }
                for c in DailyChallenge.select()
            },
            "settings": {s.key: s.value for s in Setting.select()},
        }

        # Populate daily_badges
        daily_badges_query = DailyBadge.select()
        for db in daily_badges_query:
            date_str = db.date.strftime("%Y-%m-%d")
            if date_str not in data_export["daily_badges"]:
                data_export["daily_badges"][date_str] = {}
            data_export["daily_badges"][date_str][db.badge.code] = db.count

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_export, f, indent=2, ensure_ascii=False)
