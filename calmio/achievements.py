import json
from pathlib import Path

# Load achievements catalog from JSON at import time
CATALOG_PATH = Path(__file__).resolve().parents[1] / "logros_meditacion_100.json"
with CATALOG_PATH.open("r", encoding="utf-8") as f:
    _CATALOG = json.load(f)

# Dictionary indexed by achievement id for quick lookup
ACHIEVEMENTS = {item["id"]: item for item in _CATALOG}

# Map legacy badge codes used internally to ids in the catalog
BADGE_MAP = {
    "1_breath_session": 1,
    "5_breaths_session": 2,
    "10_breaths": 3,
    "20_breaths_session": 4,
    "30_breaths_session": 5,
    "40_breaths_session": 6,
    "50_breaths_session": 7,
    "60_breaths_session": 8,
    "80_breaths_session": 9,
    "100_breaths_session": 30,
    "1_session_day": 10,
    "2_sessions_day": 27,
    "3_sessions_day": 28,
    "5_min_total": 3,
    "3_day_streak": 21,
    "7_day_streak": 22,
    "30_day_streak": 23,
}


def get_badge_info(code_or_id):
    """Return catalog entry for the given code or id."""
    if isinstance(code_or_id, str):
        badge_id = BADGE_MAP.get(code_or_id)
    else:
        badge_id = code_or_id
    return ACHIEVEMENTS.get(badge_id, {"nombre": str(code_or_id), "emoji": ""})
