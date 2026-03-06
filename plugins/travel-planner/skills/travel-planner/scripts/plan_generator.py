#!/usr/bin/env python3
"""
Travel Plan Generator

Generates detailed travel plans including itinerary, budget, and checklists.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import json
from datetime import datetime, timedelta
from typing import Any

from travel_db import get_preferences


def generate_daily_itinerary(destination: str, num_days: int, interests: list[str], pace: str = "moderate") -> list[dict[str, Any]]:
    """
    Generate a suggested daily itinerary structure.

    This is a template that should be filled with actual attractions and activities
    based on web research or user input.
    """
    itinerary = []

    for day in range(1, num_days + 1):
        day_plan = {
            "day": day,
            "date": "",  # To be filled with actual dates
            "morning": {
                "time": "9:00 AM - 12:00 PM",
                "activity": f"Activity {day}A (to be customized)",
                "type": "sightseeing",
                "duration": "3 hours",
                "notes": "Based on user interests",
            },
            "afternoon": {
                "time": "2:00 PM - 5:00 PM",
                "activity": f"Activity {day}B (to be customized)",
                "type": "experience",
                "duration": "3 hours",
                "notes": "",
            },
            "evening": {
                "time": "7:00 PM - 10:00 PM",
                "activity": f"Activity {day}C (to be customized)",
                "type": "dining",
                "duration": "2-3 hours",
                "notes": "",
            },
            "meals": {"breakfast": "Hotel/Local cafe", "lunch": "Near afternoon activity", "dinner": "Local restaurant recommendation"},
            "accommodation": "Hotel/Accommodation name",
        }

        if pace == "relaxed":
            day_plan.pop("evening")  # Fewer activities for relaxed pace

        itinerary.append(day_plan)

    return itinerary


def calculate_budget_breakdown(total_budget: float, num_days: int, accommodation_level: str = "mid-range") -> dict[str, Any]:
    """
    Generate budget breakdown by category.
    """
    # Default percentage allocations
    allocations = {
        "budget": {"accommodation": 0.40, "food": 0.25, "activities": 0.20, "transportation": 0.10, "miscellaneous": 0.05},
        "mid-range": {"accommodation": 0.35, "food": 0.25, "activities": 0.25, "transportation": 0.10, "miscellaneous": 0.05},
        "luxury": {"accommodation": 0.45, "food": 0.20, "activities": 0.20, "transportation": 0.10, "miscellaneous": 0.05},
    }

    allocation = allocations.get(accommodation_level, allocations["mid-range"])

    breakdown = {}
    for category, percentage in allocation.items():
        amount = total_budget * percentage
        per_day = amount / num_days if num_days > 0 else 0
        breakdown[category] = {"total": round(amount, 2), "per_day": round(per_day, 2), "percentage": percentage * 100}

    return {
        "total_budget": total_budget,
        "duration_days": num_days,
        "breakdown": breakdown,
        "daily_average": round(total_budget / num_days, 2) if num_days > 0 else 0,
    }


def calculate_multi_tier_budget(num_days: int, num_travelers: int, destination_region: str = "europe") -> dict[str, Any]:
    """
    Generate budget estimates for 3 tiers: budget, mid_range, premium.

    All prices in NIS. Based on typical costs for Israeli travelers.
    These are baseline estimates — actual values should be refined
    with web search data at plan generation time.
    """
    accommodation_baselines = {
        "europe": {"budget": 250, "mid_range": 450, "premium": 900},
        "asia": {"budget": 150, "mid_range": 300, "premium": 700},
        "north_america": {"budget": 350, "mid_range": 600, "premium": 1200},
        "south_america": {"budget": 180, "mid_range": 350, "premium": 750},
        "middle_east": {"budget": 200, "mid_range": 400, "premium": 850},
    }

    food_baselines = {
        "europe": {"budget": 100, "mid_range": 200, "premium": 400},
        "asia": {"budget": 60, "mid_range": 130, "premium": 300},
        "north_america": {"budget": 120, "mid_range": 220, "premium": 450},
        "south_america": {"budget": 70, "mid_range": 150, "premium": 320},
        "middle_east": {"budget": 80, "mid_range": 170, "premium": 350},
    }

    activities_baselines = {
        "europe": {"budget": 50, "mid_range": 120, "premium": 250},
        "asia": {"budget": 30, "mid_range": 80, "premium": 200},
        "north_america": {"budget": 60, "mid_range": 140, "premium": 280},
        "south_america": {"budget": 40, "mid_range": 100, "premium": 220},
        "middle_east": {"budget": 40, "mid_range": 100, "premium": 200},
    }

    region = destination_region.lower().replace(" ", "_")
    if region not in accommodation_baselines:
        region = "europe"

    tiers = {}
    for tier_name in ["budget", "mid_range", "premium"]:
        accommodation = accommodation_baselines[region][tier_name] * num_days
        food = food_baselines[region][tier_name] * num_days * num_travelers
        activities = activities_baselines[region][tier_name] * num_days * num_travelers
        total = accommodation + food + activities

        tiers[tier_name] = {
            "accommodation_per_night_nis": accommodation_baselines[region][tier_name],
            "accommodation_total_nis": accommodation,
            "food_per_day_nis": food_baselines[region][tier_name],
            "food_total_nis": food,
            "activities_per_day_nis": activities_baselines[region][tier_name],
            "activities_total_nis": activities,
            "total_nis": total,
            "per_person_nis": total / num_travelers if num_travelers > 0 else 0,
        }

    return tiers


def calculate_multi_region_budget(
    segments: list[dict[str, Any]],
    num_travelers: int,
    destination_region: str = "europe",
) -> dict[str, Any]:
    """
    Calculate budget for multi-region trips where accommodation costs vary per segment.

    Each segment dict should have:
        - region_name: str (display name)
        - nights: int
        - accommodation_multiplier: float (1.0 = standard, 1.5 = premium area, 0.8 = rural/budget area)

    Returns per-tier totals with per-segment breakdown.
    """
    region = destination_region.lower().replace(" ", "_")

    accommodation_baselines = {
        "europe": {"budget": 250, "mid_range": 450, "premium": 900},
        "asia": {"budget": 150, "mid_range": 300, "premium": 700},
        "north_america": {"budget": 350, "mid_range": 600, "premium": 1200},
        "south_america": {"budget": 180, "mid_range": 350, "premium": 750},
        "middle_east": {"budget": 200, "mid_range": 400, "premium": 850},
    }

    food_baselines = {
        "europe": {"budget": 100, "mid_range": 200, "premium": 400},
        "asia": {"budget": 60, "mid_range": 130, "premium": 300},
        "north_america": {"budget": 120, "mid_range": 220, "premium": 450},
        "south_america": {"budget": 70, "mid_range": 150, "premium": 320},
        "middle_east": {"budget": 80, "mid_range": 170, "premium": 350},
    }

    activities_baselines = {
        "europe": {"budget": 50, "mid_range": 120, "premium": 250},
        "asia": {"budget": 30, "mid_range": 80, "premium": 200},
        "north_america": {"budget": 60, "mid_range": 140, "premium": 280},
        "south_america": {"budget": 40, "mid_range": 100, "premium": 220},
        "middle_east": {"budget": 40, "mid_range": 100, "premium": 200},
    }

    if region not in accommodation_baselines:
        region = "europe"

    total_nights = sum(s["nights"] for s in segments)
    tiers = {}

    for tier_name in ["budget", "mid_range", "premium"]:
        segment_details = []
        total_accommodation = 0

        for seg in segments:
            multiplier = seg.get("accommodation_multiplier", 1.0)
            base_rate = accommodation_baselines[region][tier_name]
            adjusted_rate = base_rate * multiplier
            seg_cost = adjusted_rate * seg["nights"]
            total_accommodation += seg_cost
            segment_details.append({
                "region": seg["region_name"],
                "nights": seg["nights"],
                "rate_per_night": round(adjusted_rate),
                "subtotal": round(seg_cost),
            })

        food = food_baselines[region][tier_name] * total_nights * num_travelers
        activities = activities_baselines[region][tier_name] * total_nights * num_travelers
        total = total_accommodation + food + activities

        tiers[tier_name] = {
            "accommodation_segments": segment_details,
            "accommodation_total": round(total_accommodation),
            "food_total": round(food),
            "activities_total": round(activities),
            "total": round(total),
            "per_person": round(total / num_travelers) if num_travelers > 0 else 0,
        }

    return tiers


def format_route_comparison_table(routes: list[dict[str, Any]]) -> str:
    """
    Generate a markdown comparison table for alternative routes.

    Each route dict should have: label, flight_cost_nis, ground_cost_nis,
    hotel_range_nis, total_range_nis, door_to_door_time, recommended.
    """
    if not routes:
        return ""

    lines = []
    lines.append("| Route | Flight (NIS) | Ground (NIS) | Hotels/n (NIS) | Total/pp (NIS) | Door-to-Door |")
    lines.append("|-------|-------------|-------------|----------------|----------------|--------------|")

    for route in routes:
        label = route["label"]
        if route.get("recommended"):
            label = f"**{label}** (Recommended)"
        lines.append(
            f"| {label} "
            f"| {route['flight_cost_nis']} "
            f"| {route['ground_cost_nis']} "
            f"| {route['hotel_range_nis']} "
            f"| {route['total_range_nis']} "
            f"| {route['door_to_door_time']} |"
        )

    return "\n".join(lines)


def filter_forum_quotes(
    quotes: list[dict[str, Any]],
    reference_date: str = "",
    max_age_months: int = 24,
) -> list[dict[str, Any]]:
    """
    Filter forum quotes by recency. Quotes older than max_age_months are dropped.

    Quotes without a date field are kept (benefit of the doubt).
    reference_date should be ISO format (YYYY-MM-DD). Defaults to today.
    """
    if not quotes:
        return []

    ref = datetime.fromisoformat(reference_date) if reference_date else datetime.now()

    cutoff = ref - timedelta(days=max_age_months * 30)

    result = []
    for quote in quotes:
        date_str = quote.get("date")
        if not date_str:
            result.append(quote)
            continue
        try:
            quote_date = datetime.fromisoformat(date_str)
            if quote_date >= cutoff:
                result.append(quote)
        except (ValueError, TypeError):
            result.append(quote)

    return result


def _format_hotel_prices(prices: dict[str, Any]) -> str:
    """Format hotel price comparison line."""
    price_parts = []
    if "booking_nis" in prices:
        price_parts.append(f"Booking.com: NIS {prices['booking_nis']}/night")
    if "direct_nis" in prices and "booking_nis" in prices:
        savings_pct = round((1 - prices["direct_nis"] / prices["booking_nis"]) * 100)
        suffix = f" (save {savings_pct}%)" if savings_pct > 0 else ""
        price_parts.append(f"Direct: NIS {prices['direct_nis']}/night{suffix}")
    elif "direct_nis" in prices:
        price_parts.append(f"Direct: NIS {prices['direct_nis']}/night")
    return "Price: " + " | ".join(price_parts)


def _format_forum_quotes(quotes: list[dict[str, Any]]) -> list[str]:
    """Format forum quotes as markdown list items."""
    lines = ["", "What real travelers say:"]
    for quote in quotes:
        suffix_parts = [quote.get("source", "unknown")]
        if quote.get("votes"):
            suffix_parts.append(f"{quote['votes']} upvotes")
        if quote.get("recency"):
            suffix_parts.append(quote["recency"])
        lines.append(f'- "{quote["text"]}" -- {", ".join(suffix_parts)}')
    return lines


def _format_aggregate_scores(scores: dict[str, Any]) -> str | None:
    """Format aggregate review scores line."""
    score_parts = []
    if "booking" in scores:
        score_parts.append(f"Booking {scores['booking']}")
    if "google" in scores:
        g = scores["google"]
        score_parts.append(f"Google {g['score']} ({g['count']})")
    if "tripadvisor" in scores:
        score_parts.append(f"TripAdvisor {scores['tripadvisor']}")
    return f"Scores: {' | '.join(score_parts)}" if score_parts else None


def format_hotel_entry(hotel: dict[str, Any]) -> str:
    """
    Format a single hotel entry with forum-first reviews.

    Forum quotes appear before aggregate scores.
    Shows Booking.com vs direct price comparison when available.
    """
    tier_labels = {"budget": "Budget", "mid_range": "Mid-Range", "premium": "Premium"}
    stars_str = "*" * hotel.get("stars", 0)
    tier_label = tier_labels.get(hotel.get("tier", ""), "")

    lines = [
        f"**{hotel['name']}** {stars_str} -- {tier_label}",
        f"Location: {hotel.get('distance_to_target', 'N/A')}",
        _format_hotel_prices(hotel.get("prices", {})),
    ]

    quotes = hotel.get("forum_quotes", [])
    if quotes:
        lines.extend(_format_forum_quotes(quotes))

    scores_line = _format_aggregate_scores(hotel.get("scores", {}))
    if scores_line:
        lines.append(scores_line)

    return "\n".join(lines)


def format_car_rental_section(car_data: dict[str, Any]) -> str:
    """
    Format car rental section with forum quotes first, then comparison table.
    """
    quotes = car_data.get("forum_quotes", [])
    options = car_data.get("options", [])

    if not quotes and not options:
        return ""

    lines = []

    # Forum quotes first
    for quote in quotes:
        lines.append(f'"{quote["text"]}" -- {quote.get("source", "unknown")}')

    if quotes and options:
        lines.append("")

    # Comparison table
    if options:
        lines.append("| Company | Type | NIS/day | Total | Google | Note |")
        lines.append("|---------|------|---------|-------|--------|------|")
        for car in options:
            total = car["price_per_day_nis"] * car["num_days"]
            rating = f"{car.get('google_rating', 'N/A')} ({car.get('google_count', '')})"
            lines.append(f"| {car['company']} | {car['type']} | {car['price_per_day_nis']} | {total} | {rating} | {car.get('note', '')} |")

    return "\n".join(lines)


def format_driving_route(route: dict[str, Any]) -> str:
    """Format driving route details with optional scenic alternative."""
    hours = route["duration_min"] // 60
    mins = route["duration_min"] % 60
    duration_str = f"{hours}h{mins:02d}" if mins else f"{hours}h"

    lines = []
    lines.append(f"Route: {route['from']} -> {route['to']} ({route['distance_km']}km, {duration_str})")
    lines.append(f"Via: {route['road']}")

    cost_parts = []
    if route.get("tolls_nis"):
        cost_parts.append(f"Tolls: NIS {route['tolls_nis']}")
    if route.get("gas_estimate_nis"):
        cost_parts.append(f"Gas: ~NIS {route['gas_estimate_nis']}")
    if cost_parts:
        lines.append(" | ".join(cost_parts))

    scenic = route.get("scenic_alternative")
    if scenic:
        extra = scenic.get("extra_time_min", 0)
        lines.append("")
        lines.append(f"Scenic alternative: {scenic['road']} (+{extra}min)")
        for stop in scenic.get("stops", []):
            lines.append(f"  - Stop: {stop}")

    return "\n".join(lines)


def generate_packing_checklist(destination_climate: str, duration_days: int, trip_activities: list[str]) -> dict[str, list[str]]:
    """
    Generate packing checklist based on destination and activities.
    """
    checklist = {
        "essentials": [
            "Passport",
            "Visa (if required)",
            "Travel insurance documents",
            "Flight tickets/boarding passes",
            "Hotel confirmations",
            "Credit/debit cards",
            "Local currency",
            "Phone and charger",
            "Adapter/converter (if needed)",
            "Medications (prescription and basic)",
            "Copies of important documents",
        ],
        "clothing": [],
        "toiletries": ["Toothbrush and toothpaste", "Shampoo and soap", "Deodorant", "Sunscreen", "Any personal care items"],
        "technology": ["Phone charger", "Power bank", "Camera (if bringing)", "Headphones", "Laptop/tablet (if needed)"],
        "activities": [],
    }

    # Add climate-appropriate clothing
    if "tropical" in destination_climate.lower() or "warm" in destination_climate.lower():
        checklist["clothing"].extend(
            [
                "Lightweight, breathable clothes",
                "Shorts and t-shirts",
                "Sundress/summer clothes",
                "Swimsuit",
                "Sun hat",
                "Sunglasses",
                "Sandals/flip-flops",
            ]
        )
    elif "cold" in destination_climate.lower() or "winter" in destination_climate.lower():
        checklist["clothing"].extend(
            ["Warm jacket/coat", "Sweaters/hoodies", "Long pants", "Thermal underwear", "Warm socks", "Gloves and scarf", "Winter boots"]
        )
    else:  # Moderate/temperate
        checklist["clothing"].extend(
            [
                "Mix of light and warm layers",
                "T-shirts and long-sleeve shirts",
                "Pants and shorts",
                "Light jacket",
                "Comfortable walking shoes",
                "Sneakers",
            ]
        )

    # Add activity-specific items
    activity_items = {
        "hiking": ["Hiking boots", "Backpack", "Water bottle", "Trail snacks"],
        "beach": ["Swimsuit", "Beach towel", "Snorkel gear", "Waterproof bag"],
        "formal": ["Dress clothes", "Dress shoes", "Nice accessories"],
        "adventure": ["Athletic wear", "Action camera", "First aid kit"],
        "business": ["Business attire", "Laptop", "Business cards", "Portfolio"],
    }

    for activity in trip_activities:
        activity_lower = activity.lower()
        for key, items in activity_items.items():
            if key in activity_lower:
                checklist["activities"].extend(items)

    # Remove duplicates
    for category in checklist:
        checklist[category] = list(set(checklist[category]))

    return checklist


def generate_pre_trip_checklist(destination_country: str, departure_date: str) -> list[dict[str, Any]]:
    """
    Generate pre-trip preparation checklist with timeline.
    """
    try:
        departure = datetime.fromisoformat(departure_date)
    except (ValueError, TypeError):
        # If date parsing fails, use relative timeline
        departure = datetime.now() + timedelta(days=30)

    today = datetime.now()
    days_until = (departure - today).days

    timeline_milestones = [
        (
            90,
            "3 months before",
            [
                "Research destination and create wish list",
                "Check passport expiration (needs 6+ months validity)",
                "Research visa requirements",
                "Set up travel alerts for flights",
                "Start saving/budgeting for trip",
            ],
        ),
        (
            60,
            "2 months before",
            [
                "Book flights",
                "Book accommodation",
                "Apply for visa if needed",
                "Purchase travel insurance",
                "Check vaccination requirements",
                "Research local customs and etiquette",
            ],
        ),
        (
            30,
            "1 month before",
            [
                "Book major activities and tours",
                "Notify bank of travel dates",
                "Set up international phone plan",
                "Make restaurant reservations",
                "Check weather forecasts",
                "Start gathering packing items",
            ],
        ),
        (
            14,
            "2 weeks before",
            [
                "Confirm all reservations",
                "Print important documents",
                "Exchange some currency",
                "Refill prescriptions",
                "Arrange pet/plant care",
                "Hold mail delivery",
            ],
        ),
        (
            7,
            "1 week before",
            [
                "Check in for flights",
                "Download offline maps",
                "Pack luggage",
                "Charge all devices",
                "Clean out refrigerator",
                "Set up home security",
            ],
        ),
    ]

    checklist = []
    for min_days, timeline, tasks in timeline_milestones:
        if days_until >= min_days:
            checklist.append({"timeline": timeline, "tasks": tasks})

    # Day before
    checklist.append(
        {
            "timeline": "Day before departure",
            "tasks": [
                "Re-check flight times",
                "Prepare carry-on essentials",
                "Take out trash",
                "Check weather at destination",
                "Get good rest",
                "Set multiple alarms",
            ],
        }
    )

    return checklist


def generate_trip_plan(trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Generate complete trip plan with all components.
    """
    destination = trip_data.get("destination", {})
    duration = trip_data.get("duration_days", 7)
    budget = trip_data.get("budget", {}).get("total", 0)
    departure_date = trip_data.get("departure_date", "")

    # Get user preferences
    prefs = get_preferences()
    interests = prefs.get("interests", [])
    pace = prefs.get("pace_preference", "moderate")
    accommodation_level = prefs.get("budget_level", "mid-range")

    # Generate components
    return {
        "trip_id": trip_data.get("id", ""),
        "destination": destination,
        "dates": {"departure": trip_data.get("departure_date", ""), "return": trip_data.get("return_date", ""), "duration_days": duration},
        "itinerary": generate_daily_itinerary(destination.get("city", ""), duration, interests, pace),
        "budget": calculate_budget_breakdown(budget, duration, accommodation_level),
        "packing_checklist": generate_packing_checklist(trip_data.get("climate", "moderate"), duration, trip_data.get("activities", [])),
        "pre_trip_checklist": generate_pre_trip_checklist(destination.get("country", ""), departure_date),
        "generated_at": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate travel plan")
    parser.add_argument("--trip-id", help="Trip ID from database")
    parser.add_argument("--output", help="Output JSON file path")

    args = parser.parse_args()

    if not args.trip_id:
        print("Error: --trip-id required")
        sys.exit(1)

    from travel_db import get_trip_by_id

    trip = get_trip_by_id(args.trip_id)
    if not trip:
        print(f"Error: Trip {args.trip_id} not found")
        sys.exit(1)

    plan = generate_trip_plan(trip)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(plan, f, indent=2)
        print(f"✓ Travel plan generated: {args.output}")
    else:
        print(json.dumps(plan, indent=2))
