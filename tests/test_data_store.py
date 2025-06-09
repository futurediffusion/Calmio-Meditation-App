import sys
from pathlib import Path
from datetime import datetime, date

import pytest

# Import DataStore without triggering heavy package imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "calmio"))
from data_store import DataStore


def test_add_session_and_streak(tmp_path):
    data_file = tmp_path / "data.json"
    ds = DataStore(data_file)
    start1 = datetime(2023, 1, 1, 8, 0)
    ds.add_session(start1, seconds=60, breaths=5, inhale=3, exhale=3)

    # verify first session stored
    day_key = start1.date().isoformat()
    assert ds.data["daily_seconds"][day_key] == 60
    assert ds.get_sessions_for_date(start1)[0]["duration"] == 60

    # add second session on next day to update streak
    start2 = datetime(2023, 1, 2, 9, 0)
    ds.add_session(start2, seconds=120, breaths=6, inhale=3, exhale=3)
    assert ds.get_streak() == 2
    assert ds.get_last_session()["duration"] == 120
    assert len(ds.get_sessions_for_date(start2)) == 1


def test_weekly_summary(tmp_path):
    data_file = tmp_path / "data.json"
    ds = DataStore(data_file)

    sessions = [
        (datetime(2023, 5, 1, 10, 0), 120),  # Monday
        (datetime(2023, 5, 2, 11, 0), 300),  # Tuesday
        (datetime(2023, 5, 3, 9, 0), 60),    # Wednesday
        (datetime(2023, 5, 4, 20, 0), 180),  # Thursday
        (datetime(2023, 5, 5, 14, 0), 90),   # Friday
        # Saturday - no session
        (datetime(2023, 5, 7, 18, 0), 240),  # Sunday
    ]
    for dt, secs in sessions:
        ds.add_session(dt, seconds=secs, breaths=1, inhale=3, exhale=3)

    summary = ds.get_weekly_summary(date(2023, 5, 7))

    assert summary["minutes_per_day"] == pytest.approx([2, 5, 1, 3, 1.5, 0, 4])
    assert summary["total"] == pytest.approx(16.5)
    assert summary["average"] == pytest.approx(16.5 / 7)
    assert summary["longest_day"] == "Martes"
    assert summary["longest_time"] == "11:00"
    assert summary["longest_minutes"] == pytest.approx(5)
    assert summary["total_seconds"] == 990


def test_breath_volume_setting(tmp_path):
    data_file = tmp_path / "data.json"
    ds = DataStore(data_file)

    # default should be False
    assert ds.get_sound_setting("breath_volume", False) is False

    ds.set_sound_setting("breath_volume", True)
    assert ds.get_sound_setting("breath_volume") is True

    # ensure persistence
    ds2 = DataStore(data_file)
    assert ds2.get_sound_setting("breath_volume") is True


def test_dark_mode_setting(tmp_path):
    data_file = tmp_path / "data.json"
    ds = DataStore(data_file)

    assert ds.get_visual_setting("dark_mode", False) is False

    ds.set_visual_setting("dark_mode", True)
    assert ds.get_visual_setting("dark_mode") is True

    ds2 = DataStore(data_file)
    assert ds2.get_visual_setting("dark_mode") is True

from datetime import timedelta
from achievements import BADGE_MAP


def test_badge_awarded_and_lookup(tmp_path):
    data_file = tmp_path / "data.json"
    ds = DataStore(data_file)
    start = datetime(2023, 1, 1, 8, 0)
    ds.add_session(start, seconds=300, breaths=10, inhale=3, exhale=3)
    badges = ds.get_badges_for_date(start)
    assert BADGE_MAP["5_min_total"] in badges
    assert BADGE_MAP["1_breath_session"] in badges


def test_three_day_streak_badge(tmp_path):
    data_file = tmp_path / "data.json"
    ds = DataStore(data_file)
    start = datetime(2023, 1, 1, 8, 0)
    for i in range(3):
        ds.add_session(start + timedelta(days=i), seconds=60, breaths=1, inhale=3, exhale=3)
    third_day_badges = ds.get_badges_for_date(start + timedelta(days=2))
    assert BADGE_MAP["3_day_streak"] in third_day_badges
