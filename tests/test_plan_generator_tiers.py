import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "travel-planner", "scripts"))

from plan_generator import calculate_multi_tier_budget


def test_multi_tier_budget_returns_three_tiers():
    result = calculate_multi_tier_budget(num_days=4, num_travelers=2, destination_region="europe")

    assert "budget" in result
    assert "mid_range" in result
    assert "premium" in result

    # Each tier has required fields
    for tier_name in ["budget", "mid_range", "premium"]:
        tier = result[tier_name]
        assert "accommodation_per_night_nis" in tier
        assert "food_per_day_nis" in tier
        assert "activities_per_day_nis" in tier
        assert "total_nis" in tier
        assert "per_person_nis" in tier

    # Budget < mid_range < premium
    assert result["budget"]["total_nis"] < result["mid_range"]["total_nis"]
    assert result["mid_range"]["total_nis"] < result["premium"]["total_nis"]


def test_multi_tier_budget_per_person_correct():
    result = calculate_multi_tier_budget(num_days=4, num_travelers=2, destination_region="europe")

    for tier_name in ["budget", "mid_range", "premium"]:
        tier = result[tier_name]
        assert tier["per_person_nis"] == tier["total_nis"] / 2
