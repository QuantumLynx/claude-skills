import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "travel-planner", "scripts"))

import travel_db
from plan_generator import calculate_multi_tier_budget


# ============================================================================
# Bug 1: ZeroDivisionError in calculate_multi_tier_budget
# ============================================================================


def test_multi_tier_budget_zero_travelers_no_crash():
    """calculate_multi_tier_budget must not crash when num_travelers=0."""
    result = calculate_multi_tier_budget(num_days=4, num_travelers=0)
    assert isinstance(result, dict)
    for tier in ["budget", "mid_range", "premium"]:
        assert tier in result
        assert result[tier]["per_person_nis"] == 0


def test_multi_tier_budget_zero_days_no_crash():
    """calculate_multi_tier_budget must not crash when num_days=0."""
    result = calculate_multi_tier_budget(num_days=0, num_travelers=2)
    assert isinstance(result, dict)
    for tier in ["budget", "mid_range", "premium"]:
        assert result[tier]["total_nis"] == 0


# ============================================================================
# Bug 2: Status inconsistency — "idea" vs "ideas"
# ============================================================================


def test_get_trips_accepts_idea_singular(tmp_path):
    """get_trips('idea') should return trip_ideas, same as 'ideas'."""
    _setup_temp_db(tmp_path)
    trip = {"destination": {"city": "Tokyo", "country": "Japan"}, "departure_date": "2026-09-01"}
    travel_db.add_trip(trip, status="idea")

    result_singular = travel_db.get_trips("idea")
    result_plural = travel_db.get_trips("ideas")

    assert "trip_ideas" in result_singular
    assert "trip_ideas" in result_plural
    assert len(result_singular["trip_ideas"]) == 1
    assert len(result_plural["trip_ideas"]) == 1


# ============================================================================
# Bug 3: Invalid status silently drops trip
# ============================================================================


def test_add_trip_invalid_status_raises(tmp_path):
    """add_trip with invalid status should raise ValueError."""
    _setup_temp_db(tmp_path)
    trip = {"destination": {"city": "Berlin", "country": "Germany"}}

    try:
        travel_db.add_trip(trip, status="invalid_status")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# ============================================================================
# Helpers
# ============================================================================


def _setup_temp_db(tmp_path):
    travel_db.DB_DIR = tmp_path
    travel_db.PREFERENCES_FILE = tmp_path / "preferences.json"
    travel_db.TRIPS_FILE = tmp_path / "trips.json"
    travel_db.ensure_db_files()
