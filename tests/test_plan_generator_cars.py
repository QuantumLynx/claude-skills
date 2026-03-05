import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins", "travel-planner", "skills", "travel-planner", "scripts"))

from plan_generator import format_car_rental_section


def test_format_car_rental_with_quotes_and_table():
    cars = {
        "forum_quotes": [
            {"text": "Sixt from MUC is smooth, no hidden fees.", "source": "r/travel"},
            {"text": "Avoid Europcar MUC.", "source": "r/TravelHacks"},
        ],
        "options": [
            {
                "company": "Sixt",
                "type": "Compact",
                "price_per_day_nis": 170,
                "num_days": 4,
                "google_rating": 4.6,
                "google_count": 2100,
                "note": "Forum favorite",
            },
            {
                "company": "Enterprise",
                "type": "Economy",
                "price_per_day_nis": 145,
                "num_days": 4,
                "google_rating": 4.3,
                "google_count": 890,
                "note": "Budget pick",
            },
        ],
    }

    result = format_car_rental_section(cars)

    assert "Sixt" in result
    assert "Enterprise" in result
    assert "r/travel" in result
    assert "170" in result
    assert "|" in result  # markdown table
    assert "Forum favorite" in result


def test_format_car_rental_empty():
    result = format_car_rental_section({"forum_quotes": [], "options": []})
    assert result == ""
