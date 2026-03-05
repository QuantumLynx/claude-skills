import os
import sys

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "travel-planner", "scripts"))

import travel_db


def setup_temp_db(tmp_path):
    """Point travel_db at a temp directory."""
    travel_db.DB_DIR = tmp_path
    travel_db.PREFERENCES_FILE = tmp_path / "preferences.json"
    travel_db.TRIPS_FILE = tmp_path / "trips.json"
    travel_db.ensure_db_files()


def test_add_trip_with_routes(tmp_path):
    setup_temp_db(tmp_path)

    trip = {
        "destination": {"city": "Salzburg", "country": "Austria", "region": "Salzburg"},
        "departure_date": "2026-06-15",
        "return_date": "2026-06-19",
        "duration_days": 4,
        "budget": {"total": 5000, "currency": "NIS"},
        "travelers": 2,
        "routes": [
            {
                "id": "route_1",
                "label": "TLV -> Munich + car",
                "recommended": True,
                "flight_airport": "MUC",
                "ground_transport": {"type": "car", "distance_km": 145, "duration_min": 100, "estimated_cost_nis": 170},
            },
            {
                "id": "route_2",
                "label": "TLV -> Vienna + train",
                "recommended": False,
                "flight_airport": "VIE",
                "ground_transport": {"type": "train", "distance_km": 300, "duration_min": 150, "estimated_cost_nis": 95},
            },
        ],
        "budget_tiers": {
            "budget": {"total_nis": 3500, "per_person_nis": 1750},
            "mid_range": {"total_nis": 5000, "per_person_nis": 2500},
            "premium": {"total_nis": 8000, "per_person_nis": 4000},
        },
        "currency": {"primary": "NIS", "secondary": "EUR", "rate_date": "2026-06-01"},
    }

    trip_id = travel_db.add_trip(trip, status="current")
    assert trip_id is not None

    retrieved = travel_db.get_trip_by_id(trip_id)
    assert retrieved is not None
    expected_route_count = 2
    assert len(retrieved["routes"]) == expected_route_count
    assert retrieved["routes"][0]["recommended"] is True
    expected_per_person = 2500
    assert retrieved["budget_tiers"]["mid_range"]["per_person_nis"] == expected_per_person
    assert retrieved["currency"]["primary"] == "NIS"


def test_add_trip_without_routes_still_works(tmp_path):
    """Existing trips without routes field should still work."""
    setup_temp_db(tmp_path)

    trip = {
        "destination": {"city": "Barcelona", "country": "Spain"},
        "departure_date": "2026-07-01",
        "return_date": "2026-07-08",
        "duration_days": 7,
        "budget": {"total": 2500, "currency": "USD"},
        "travelers": 2,
    }

    trip_id = travel_db.add_trip(trip, status="current")
    retrieved = travel_db.get_trip_by_id(trip_id)
    assert retrieved is not None
    assert "routes" not in retrieved  # No routes field added if not provided
