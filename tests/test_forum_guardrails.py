import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "travel-planner", "scripts"))

from plan_generator import filter_forum_quotes


def test_filter_removes_old_quotes():
    """Quotes older than max_age_months should be filtered out."""
    quotes = [
        {"text": "Great hotel!", "source": "r/travel", "date": "2026-01-15"},
        {"text": "Terrible hotel!", "source": "r/travel", "date": "2022-01-01"},
    ]
    result = filter_forum_quotes(quotes, reference_date="2026-03-05", max_age_months=24)
    assert len(result) == 1
    assert result[0]["text"] == "Great hotel!"


def test_filter_keeps_all_recent():
    """All recent quotes should be kept."""
    quotes = [
        {"text": "Quote A", "source": "r/travel", "date": "2025-12-01"},
        {"text": "Quote B", "source": "Reddit", "date": "2026-02-01"},
    ]
    result = filter_forum_quotes(quotes, reference_date="2026-03-05", max_age_months=24)
    assert len(result) == 2


def test_filter_handles_missing_date():
    """Quotes without dates should be kept (benefit of the doubt)."""
    quotes = [
        {"text": "No date quote", "source": "r/travel"},
        {"text": "Dated quote", "source": "r/travel", "date": "2020-01-01"},
    ]
    result = filter_forum_quotes(quotes, reference_date="2026-03-05", max_age_months=24)
    assert len(result) == 1
    assert result[0]["text"] == "No date quote"


def test_filter_empty_list():
    """Empty input returns empty output."""
    assert filter_forum_quotes([], reference_date="2026-03-05") == []


def test_filter_default_max_age():
    """Default max_age_months is 24."""
    quotes = [
        {"text": "Recent", "source": "r/travel", "date": "2025-06-01"},
        {"text": "Old", "source": "r/travel", "date": "2023-01-01"},
    ]
    result = filter_forum_quotes(quotes, reference_date="2026-03-05")
    assert len(result) == 1
    assert result[0]["text"] == "Recent"
