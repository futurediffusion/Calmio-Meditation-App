from pathlib import Path
from datetime import datetime, date, timedelta
import pytest
from peewee import SqliteDatabase

from calmio.data_store import DataStore
from calmio.database import (
    Setting,
    Session,
    Badge,
    DailyBadge,
    DailyChallenge,
    BaseModel,
)
from calmio.achievements import BADGE_MAP


@pytest.fixture
def test_db():
    """Fixture to use an in-memory SQLite database for tests."""
    test_db = SqliteDatabase(":memory:")
    models = [Setting, Session, Badge, DailyBadge, DailyChallenge, BaseModel]
    test_db.bind(models, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(models)
    yield test_db
    test_db.drop_tables(models)
    test_db.close()


@pytest.fixture
def ds(test_db):
    """Fixture to provide a DataStore instance initialized with the test database."""
    return DataStore()


def test_add_session_and_streak(ds):
    start1 = datetime(2023, 1, 1, 8, 0)
    ds.add_session(start1, seconds=60, breaths=5, inhale=3, exhale=3)

    # Verify first session stored
    ds.now = lambda: start1
    assert ds.get_today_seconds() == 60
    assert ds.get_sessions_for_date(start1)[0]["duration"] == 60

    # Add second session on the next day to update streak
    start2 = datetime(2023, 1, 2, 9, 0)
    ds.add_session(start2, seconds=120, breaths=6, inhale=3, exhale=3)
    ds.now = lambda: start2
    assert ds.get_streak() == 2
    assert ds.get_last_session()["duration"] == 120
    assert len(ds.get_sessions_for_date(start2)) == 1


def test_weekly_summary(ds):
    sessions = [
        (datetime(2023, 5, 1, 10, 0), 120),  # Monday
        (datetime(2023, 5, 2, 11, 0), 300),  # Tuesday
        (datetime(2023, 5, 3, 9, 0), 60),  # Wednesday
        (datetime(2023, 5, 4, 20, 0), 180),  # Thursday
        (datetime(2023, 5, 5, 14, 0), 90),  # Friday
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


def test_breath_volume_setting(ds):
    # Default should be False
    assert ds.get_sound_setting("breath_volume", False) is False

    ds.set_sound_setting("breath_volume", True)
    assert ds.get_sound_setting("breath_volume") is True

    # Ensure persistence
    assert ds.get_sound_setting("breath_volume") is True


def test_dark_mode_setting(ds):
    assert ds.get_visual_setting("dark_mode", False) is False

    ds.set_visual_setting("dark_mode", True)
    assert ds.get_visual_setting("dark_mode") is True

    # Ensure persistence
    assert ds.get_visual_setting("dark_mode") is True


def test_badge_awarded_and_lookup(ds):
    start = datetime(2023, 1, 1, 8, 0)
    ds.add_session(start, seconds=300, breaths=10, inhale=3, exhale=3)
    badges = ds.get_badges_for_date(start)
    assert str(BADGE_MAP["5_min_total"]) in badges
    assert str(BADGE_MAP["1_breath_session"]) in badges


def test_three_day_streak_badge(ds):
    start = datetime(2023, 1, 1, 8, 0)
    for i in range(3):
        session_time = start + timedelta(days=i)
        ds.add_session(session_time, seconds=60, breaths=1, inhale=3, exhale=3)
        ds.now = lambda: session_time
        assert ds.get_streak() == i + 1

    third_day_badges = ds.get_badges_for_date(start + timedelta(days=2))
    assert str(BADGE_MAP["3_day_streak"]) in third_day_badges


def test_daily_challenge_persistence(ds):
    challenge_date = date(2023, 1, 1)
    ds.set_daily_challenge("Respira", challenge_date)
    ch = ds.get_challenge_for_date(challenge_date)
    assert ch["text"] == "Respira"
    assert ch["completed"] is False

    ds.mark_challenge_completed(challenge_date)
    ch2 = ds.get_challenge_for_date(challenge_date)
    assert ch2["completed"] is True

    # Ensure persistence
    ch3 = ds.get_challenge_for_date(challenge_date)
    assert ch3["completed"] is True
