import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "travel-planner", "scripts"))

from plan_generator import format_driving_route


def test_format_driving_route_with_scenic():
    route = {
        "from": "Munich Airport",
        "to": "Salzburg Old Town",
        "distance_km": 145,
        "duration_min": 100,
        "road": "A8 autobahn",
        "tolls_nis": 38,
        "gas_estimate_nis": 55,
        "scenic_alternative": {
            "road": "B305 through Berchtesgaden",
            "extra_time_min": 40,
            "stops": ["Konigsee lake (30min detour)", "Eagle's Nest (seasonal May-Oct)"],
        },
    }

    result = format_driving_route(route)

    assert "Munich Airport" in result
    assert "Salzburg" in result
    assert "145" in result
    assert "A8" in result
    assert "Berchtesgaden" in result
    assert "Konigsee" in result


def test_format_driving_route_without_scenic():
    route = {
        "from": "Vienna Airport",
        "to": "Salzburg",
        "distance_km": 300,
        "duration_min": 180,
        "road": "A1 Westautobahn",
        "tolls_nis": 38,
        "gas_estimate_nis": 90,
    }

    result = format_driving_route(route)

    assert "Vienna Airport" in result
    assert "300" in result
    assert "scenic" not in result.lower()
