import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins", "travel-planner", "skills", "travel-planner", "scripts"))

from plan_generator import calculate_multi_region_budget


ITALY_SEGMENTS = [
    {"region_name": "Dolomites", "nights": 5, "accommodation_multiplier": 1.3},
    {"region_name": "Tuscany", "nights": 4, "accommodation_multiplier": 0.9},
    {"region_name": "Florence", "nights": 2, "accommodation_multiplier": 1.1},
    {"region_name": "Rome", "nights": 2, "accommodation_multiplier": 1.0},
]


def test_returns_three_tiers():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    assert set(result.keys()) == {"budget", "mid_range", "premium"}


def test_tier_has_required_fields():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        tier = result[tier_name]
        assert "accommodation_segments" in tier
        assert "accommodation_total" in tier
        assert "food_total" in tier
        assert "activities_total" in tier
        assert "total" in tier
        assert "per_person" in tier


def test_budget_less_than_mid_less_than_premium():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    assert result["budget"]["total"] < result["mid_range"]["total"]
    assert result["mid_range"]["total"] < result["premium"]["total"]


def test_per_person_is_total_divided_by_travelers():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        tier = result[tier_name]
        assert tier["per_person"] == round(tier["total"] / 4)


def test_segment_count_matches_input():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        segments = result[tier_name]["accommodation_segments"]
        assert len(segments) == 4
        assert segments[0]["region"] == "Dolomites"
        assert segments[1]["region"] == "Tuscany"
        assert segments[2]["region"] == "Florence"
        assert segments[3]["region"] == "Rome"


def test_segment_nights_match_input():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        segments = result[tier_name]["accommodation_segments"]
        assert segments[0]["nights"] == 5
        assert segments[1]["nights"] == 4
        assert segments[2]["nights"] == 2
        assert segments[3]["nights"] == 2


def test_multiplier_affects_rate():
    """Higher multiplier = higher rate per night for the same tier."""
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        segments = result[tier_name]["accommodation_segments"]
        # Dolomites (1.3x) should cost more per night than Rome (1.0x)
        assert segments[0]["rate_per_night"] > segments[3]["rate_per_night"]
        # Tuscany (0.9x) should cost less per night than Rome (1.0x)
        assert segments[1]["rate_per_night"] < segments[3]["rate_per_night"]


def test_accommodation_total_equals_sum_of_segments():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        tier = result[tier_name]
        seg_sum = sum(s["subtotal"] for s in tier["accommodation_segments"])
        assert tier["accommodation_total"] == seg_sum


def test_total_equals_accommodation_plus_food_plus_activities():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        tier = result[tier_name]
        expected = tier["accommodation_total"] + tier["food_total"] + tier["activities_total"]
        assert tier["total"] == expected


def test_food_scales_with_travelers_and_nights():
    """Food cost should double when travelers double."""
    r2 = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=2)
    r4 = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        assert r4[tier_name]["food_total"] == r2[tier_name]["food_total"] * 2


def test_accommodation_does_not_scale_with_travelers():
    """Accommodation is per-room, not per-person — should NOT change with traveler count."""
    r2 = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=2)
    r4 = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=4)
    for tier_name in ["budget", "mid_range", "premium"]:
        assert r4[tier_name]["accommodation_total"] == r2[tier_name]["accommodation_total"]


def test_unknown_region_falls_back_to_europe():
    result = calculate_multi_region_budget(
        [{"region_name": "X", "nights": 3, "accommodation_multiplier": 1.0}],
        num_travelers=2,
        destination_region="atlantis",
    )
    europe = calculate_multi_region_budget(
        [{"region_name": "X", "nights": 3, "accommodation_multiplier": 1.0}],
        num_travelers=2,
        destination_region="europe",
    )
    assert result == europe


def test_single_segment():
    result = calculate_multi_region_budget(
        [{"region_name": "Paris", "nights": 5, "accommodation_multiplier": 1.0}],
        num_travelers=2,
    )
    for tier_name in ["budget", "mid_range", "premium"]:
        assert len(result[tier_name]["accommodation_segments"]) == 1
        assert result[tier_name]["accommodation_segments"][0]["nights"] == 5


def test_default_multiplier_is_one():
    """Segment without accommodation_multiplier should default to 1.0."""
    with_default = calculate_multi_region_budget(
        [{"region_name": "X", "nights": 3}],
        num_travelers=2,
    )
    with_explicit = calculate_multi_region_budget(
        [{"region_name": "X", "nights": 3, "accommodation_multiplier": 1.0}],
        num_travelers=2,
    )
    assert with_default == with_explicit


def test_zero_travelers_returns_zero_per_person():
    result = calculate_multi_region_budget(ITALY_SEGMENTS, num_travelers=0)
    for tier_name in ["budget", "mid_range", "premium"]:
        assert result[tier_name]["per_person"] == 0


def test_asia_region_cheaper_than_europe():
    europe = calculate_multi_region_budget(
        [{"region_name": "X", "nights": 5, "accommodation_multiplier": 1.0}],
        num_travelers=2,
        destination_region="europe",
    )
    asia = calculate_multi_region_budget(
        [{"region_name": "X", "nights": 5, "accommodation_multiplier": 1.0}],
        num_travelers=2,
        destination_region="asia",
    )
    for tier_name in ["budget", "mid_range", "premium"]:
        assert asia[tier_name]["total"] < europe[tier_name]["total"]
