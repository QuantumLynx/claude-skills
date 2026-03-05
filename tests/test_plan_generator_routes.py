import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "travel-planner", "scripts"))

from plan_generator import format_route_comparison_table


def test_format_route_comparison_returns_markdown():
    routes = [
        {
            "label": "TLV -> Munich + car",
            "flight_cost_nis": 450,
            "ground_cost_nis": 170,
            "hotel_range_nis": "250-900",
            "total_range_nis": "1520-2850",
            "door_to_door_time": "5h",
            "recommended": True,
        },
        {
            "label": "TLV -> Vienna + train",
            "flight_cost_nis": 680,
            "ground_cost_nis": 95,
            "hotel_range_nis": "280-950",
            "total_range_nis": "1780-3100",
            "door_to_door_time": "6.5h",
            "recommended": False,
        },
    ]

    result = format_route_comparison_table(routes)

    assert isinstance(result, str)
    assert "Munich" in result
    assert "Vienna" in result
    assert "Recommended" in result or "recommended" in result.lower()
    assert "|" in result  # markdown table


def test_format_route_comparison_empty_list():
    result = format_route_comparison_table([])
    assert result == ""
