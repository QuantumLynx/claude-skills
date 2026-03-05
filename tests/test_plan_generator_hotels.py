import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "travel-planner", "scripts"))

from plan_generator import format_hotel_entry


def test_format_hotel_entry_with_all_fields():
    hotel = {
        "name": "Hotel Alpenrose",
        "stars": 4,
        "tier": "mid_range",
        "distance_to_target": "200m from Old Town",
        "prices": {
            "booking_nis": 420,
            "direct_nis": 385,
            "direct_url": "https://alpenrose.at",
        },
        "forum_quotes": [
            {"text": "Best value in Salzburg.", "source": "r/travel", "votes": 47},
            {"text": "Street noise on weekends.", "source": "Google Maps", "recency": "3 months ago"},
        ],
        "scores": {
            "booking": 8.7,
            "google": {"score": 4.5, "count": 890},
            "tripadvisor": 4.4,
        },
    }

    result = format_hotel_entry(hotel)

    assert "Hotel Alpenrose" in result
    assert "200m from Old Town" in result
    assert "420" in result  # booking price
    assert "385" in result  # direct price
    assert "save" in result.lower()  # savings note
    assert "Best value in Salzburg" in result
    assert "r/travel" in result
    assert "8.7" in result  # booking score


def test_format_hotel_entry_without_direct_price():
    hotel = {
        "name": "Budget Hostel",
        "stars": 2,
        "tier": "budget",
        "distance_to_target": "500m from center",
        "prices": {"booking_nis": 200},
        "forum_quotes": [
            {"text": "Clean and cheap.", "source": "r/solotravel"},
        ],
        "scores": {"google": {"score": 4.2, "count": 300}},
    }

    result = format_hotel_entry(hotel)

    assert "Budget Hostel" in result
    assert "200" in result
    assert "save" not in result.lower()  # no savings when no direct price
