---
name: travel-planner
description: This skill should be used whenever users need help planning trips, creating travel itineraries, managing travel budgets, or seeking destination advice. On first use, collects comprehensive travel preferences including budget level, travel style, interests, and dietary restrictions. Generates detailed travel plans with day-by-day itineraries, budget breakdowns, packing checklists, cultural do's and don'ts, and region-specific schedules. Maintains database of preferences and past trips for personalized recommendations.
---

# Travel Planner

## Overview

This skill transforms Claude into a comprehensive travel planning assistant that maintains your travel preferences and generates detailed, personalized trip plans including itineraries, budget breakdowns, packing lists, and cultural guidelines for any destination.

## When to Use This Skill

Invoke this skill for travel-related tasks:
- Planning trips and creating itineraries
- Budget planning and expense tracking
- Destination research and recommendations
- Packing checklists
- Cultural etiquette and do's/don'ts
- Pre-trip preparation timelines
- Travel preference management

## Workflow

### Step 1: Check for Existing Preferences

Check if travel preferences exist:

```bash
python3 scripts/travel_db.py is_initialized
```

If "false", proceed to Step 2 (Setup). If "true", proceed to Step 3 (Trip Planning).

### Step 2: Initial Preference Collection

When no preferences exist, collect comprehensive travel information:

**Travel Style & Budget:**
- Budget level: budget, mid-range, luxury
- Travel pace: relaxed, moderate, packed
- Accommodation preferences: hostel, hotel, Airbnb, resort
- Travel companions: solo, couple, family, group

**Interests & Activities:**
- Sightseeing & landmarks
- Food & culinary experiences
- Adventure & outdoor activities
- Culture & history
- Beach & relaxation
- Nightlife & entertainment
- Shopping
- Nature & wildlife
- Photography
- Wellness & spa

**Dietary & Health:**
- Dietary restrictions (vegetarian, vegan, allergies)
- Accessibility needs
- Health considerations
- Fitness level

**Languages & Skills:**
- Languages spoken
- Travel experience level
- Comfort with adventure

**Previous Travel:**
- Countries/cities visited
- Favorite destinations
- Bucket list destinations

**Saving Preferences:**

```python
import sys
sys.path.append('[SKILL_DIR]/scripts')
from travel_db import save_preferences

preferences = {
    "travel_style": "adventurous",
    "budget_level": "mid-range",
    "accommodation_preference": ["boutique hotels", "Airbnb"],
    "interests": ["culture", "food", "hiking", "photography"],
    "dietary_restrictions": ["vegetarian"],
    "pace_preference": "moderate",
    "travel_companions": "couple",
    "language_skills": ["English", "Spanish"],
    "previous_destinations": ["Paris", "Tokyo", "Barcelona"],
    "bucket_list": [
        {"destination": "New Zealand", "notes": "Lord of the Rings locations"},
        {"destination": "Peru", "notes": "Machu Picchu"}
    ]
}

save_preferences(preferences)
```

Replace `[SKILL_DIR]` with actual skill path.

### Step 3: Create New Trip

When user wants to plan a trip, gather:

**Essential Information:**
1. **Destination**: City/country
2. **Dates**: Departure and return dates (or flexible date range)
3. **Duration**: Number of days
4. **Budget**: Total budget or daily budget
5. **Purpose**: Vacation, business, special occasion
6. **Must-see/do**: Specific attractions or activities

**Creating Trip:**

```python
from travel_db import add_trip

trip = {
    "destination": {
        "city": "Barcelona",
        "country": "Spain",
        "region": "Catalonia"
    },
    "departure_date": "2025-06-15",
    "return_date": "2025-06-22",
    "duration_days": 7,
    "budget": {
        "total": 2500,
        "currency": "USD"
    },
    "purpose": "vacation",
    "travelers": 2,
    "climate": "warm Mediterranean",
    "activities": ["sightseeing", "food tours", "beach", "architecture"],
    "accommodation": {
        "type": "boutique hotel",
        "location": "Gothic Quarter"
    }
}

trip_id = add_trip(trip, status="current")
```

### Step 4: Alternative Route Discovery

Before researching the destination in depth, search for alternative travel routes.
The goal: find cheaper or more convenient ways to reach the destination.

**Process:**
1. WebSearch: "airports within 500km of {destination city}" (500km catches hubs like Bratislava, Ljubljana, Bologna)
2. WebSearch: "cheapest flights from Tel Aviv to {country} {month} {year}"
3. WebSearch: "Wizz Air Ryanair TLV to {country} {month} {year}" (LCC carriers often have unpublished deals)
4. WebSearch: "{nearby airport} to {destination} transport options car train"

**LCC Carrier Strategy (from TLV):**
- **Wizz Air**: Budapest, Vienna, Rome, Sofia, Bucharest, Larnaca — baggage fees change pricing significantly
- **Ryanair**: Paphos, Milan BGY, Rome CIA — check secondary airports
- Always calculate total cost WITH checked bag (22kg) — LCC "base fare" is misleading

For each candidate airport (max 4), estimate:
- Flight cost from TLV (NIS) — include checked bag for LCC
- Ground transport cost + time to final destination
- Total cost comparison

**Example for Salzburg, Austria:**
- Munich (MUC): cheap flights (Wizz Air/Lufthansa), 1h40 drive, scenic route through Alps
- Vienna (VIE): more flights available (Wizz Air/Austrian), 3h train
- Ljubljana (LJU): Wizz Air direct, 3h drive through Alps — scenic but longer
- Salzburg (SZG): connecting flights only, most expensive

**Select top 3 routes** and save to trip data:

```python
from travel_db import update_trip

routes = [
    {
        "id": "route_1",
        "label": "TLV -> Munich + rental car",
        "recommended": True,
        "flight_airport": "MUC",
        "ground_transport": {
            "type": "car",
            "distance_km": 145,
            "duration_min": 100,
            "estimated_cost_nis": 170
        }
    },
    # ... more routes
]

update_trip(trip_id, {"routes": routes})
```

Present routes to user with comparison table (use `format_route_comparison_table` from `plan_generator.py`) and your recommendation. Wait for user confirmation before proceeding.

### Step 5: Review-Based Search (Hotels & Car Rentals)

For each viable route, search for hotels and car rentals using FORUM-FIRST approach.

**Review Source Priority (forums first, aggregators second):**
1. Israeli travel forums (FlyTalk.co.il, Lametayel.co.il) — Hebrew-language, Israel-specific tips
2. Reddit (r/travel, r/solotravel, r/TravelHacks, r/IsraelTravel, destination subs)
3. Travel forums (Lonely Planet Thorn Tree, FlyerTalk, TripAdvisor forum posts)
4. Google Maps reviews (local voices, recent experiences)
5. TripAdvisor/Booking.com scores (secondary data point only)

**Forum Guardrails — MANDATORY:**
- **Recency**: Only use quotes from the last 24 months. Use `filter_forum_quotes()` from `plan_generator.py` to enforce.
- **Triangulation**: A claim needs 3+ independent sources to be presented as fact. Single-source opinions must be attributed ("one Redditor says...").
- **Credibility scoring**: Prefer posts with high upvotes/engagement. Flag accounts with no history.

**Hotel Search:**

Search queries:
- `site:flytalk.co.il "{destination}" מלון` (Israeli forum, Hebrew)
- `site:lametayel.co.il "{destination}"` (Israeli travelers forum)
- `site:reddit.com "{destination}" hotel recommendation`
- `site:reddit.com "{destination}" where to stay`
- `"{destination}" best hotel review site:tripadvisor.com/ShowTopic`
- `"{destination}" hotels near {target area} site:booking.com`
- Check hotel direct websites for lower prices

Selection criteria (in order):
1. **Proximity to target** (weighted highest) - walking distance to main area
2. **Forum sentiment** - real quotes from Reddit/forums
3. **Review scores** - Booking.com 8.5+, Google Maps 4.3+, TripAdvisor 4.0+

Find 2-3 hotels per budget tier:
- Budget: NIS 150-300/night
- Mid-Range: NIS 300-600/night
- Premium: NIS 600-1200/night

Also search for 1 Airbnb alternative per tier.

**Car Rental Search:**

Search queries:
- `site:flytalk.co.il "{airport/city}" השכרת רכב` (Israeli forum, Hebrew)
- `site:reddit.com "{airport/city}" car rental recommendation`
- `site:reddit.com "{airport/city}" rent car avoid`
- `"{city}" car rental google maps reviews`

Preference: local companies with Google Maps 4.5+ over international chains.
Include: daily rate, insurance notes (CDW/SCDW coverage, excess amounts), pickup/dropoff, customer complaints.

**Insurance Note for Israeli Drivers:**
- CDW (Collision Damage Waiver) is essential — verify excess amount (typically EUR 800-1500)
- SCDW (Super CDW) reduces excess to zero — often worth the extra NIS 30-50/day
- Check if Israeli credit card provides rental car insurance (Visa Platinum, Amex often do)
- IDP (International Driving Permit) required in some countries — check before departure

**Booking Source Priority for Hotels:**
1. Booking.com (primary for availability/pricing, 8.5+ filter)
2. Hotel direct website (check if cheaper - often 5-15% savings)
3. Airbnb (alternative option, especially families/longer stays)

Always show both Booking.com price and direct price when available.

Format hotels using `format_hotel_entry` and car rentals using `format_car_rental_section` from `plan_generator.py`.

### Step 6: Research Destination

Use web search to gather current information:

**Essential Research:**
1. **Entry Requirements** - Visa, passport, vaccinations
2. **Best Time to Visit** - Weather, seasons, festivals
3. **Safety Information** - Travel advisories, safe areas, common scams
4. **Cultural Norms** - Do's and don'ts (use `references/cultural_etiquette.md` as guide)
5. **Local Transportation** - Metro, buses, taxis, apps
6. **Top Attractions** - Must-see places with hours and prices
7. **Food Recommendations** - Local specialties, popular restaurants
8. **Neighborhoods** - Where to stay, where to explore
9. **Day Trip Options** - Nearby attractions
10. **Practical Info** - Currency, tipping, power outlets, language

**Search Topics to Cover:**
- "[Destination] visa requirements for [nationality]"
- "[Destination] best time to visit weather"
- "[Destination] cultural do's and don'ts"
- "[Destination] top attractions and activities"
- "[Destination] local transportation guide"
- "[Destination] where to stay neighborhoods"
- "[Destination] food and restaurants"
- "[Destination] scams to avoid"
- "[Destination] budget guide"

### Step 7: Generate Detailed Travel Plan

Generate the full report using the template in `references/report_template.md`.

**Report structure:**

1. **Route Comparison Table** - Use `format_route_comparison_table()` at the top
2. **Per-Route Sections** - For each viable route:
   - Flights table (airline, route, NIS/pp, with bag, departure)
   - Car rental section with forum quotes - use `format_car_rental_section()`
   - Hotels by tier (Budget / Mid-Range / Premium) - use `format_hotel_entry()`
   - Airbnb alternatives
   - Driving details - use `format_driving_route()`
3. **Day-by-Day Itinerary** - Based on recommended route, using user's pace preference
4. **Budget Breakdown by Tier** - Use `calculate_multi_tier_budget()` for baselines, refine with actual web search data

```python
from plan_generator import calculate_multi_tier_budget

tiers = calculate_multi_tier_budget(
    num_days=4,
    num_travelers=2,
    destination_region="europe"
)
```

5. **Booking Tips Table** - When to book, where, and tips
6. **Cultural Do's and Don'ts** - Use `references/cultural_etiquette.md` template
7. **Pre-Trip Preparation Timeline** - Use `generate_pre_trip_checklist()`
8. **Packing Checklist** - Use `generate_packing_checklist()`
9. **Emergency & Practical Info** - Numbers, embassy, currency, voltage, tipping

**Pricing rules:**
- All prices in NIS first, secondary currency in parentheses
- Show per-person AND total amounts
- Include rate date for currency conversions

**Itinerary rules:**
- Based on recommended route
- Logical geographic grouping
- Realistic timing with buffers
- Mix of activity types
- Meal suggestions with NIS prices
- Transportation details between activities

### Step 8: Track Trip and Budget

During the trip, track expenses:

```python
from travel_db import add_expense

expense = {
    "category": "food",
    "amount": 45.00,
    "currency": "NIS",
    "description": "Dinner at Cerveceria Catalana",
    "date": "2026-06-16"
}

add_expense(trip_id, expense)
```

View budget status:

```python
from travel_db import get_budget_summary

summary = get_budget_summary(trip_id)
# Shows: total_budget, spent, remaining, percentage_used, by_category
```

### Step 9: Post-Trip Updates

After trip, move to past trips and update:

```python
from travel_db import move_trip_to_past, add_previous_destination

move_trip_to_past(trip_id)
add_previous_destination("Salzburg, Austria")
```

## Best Practices

1. **Forum-First Research** - Reddit/forum quotes over aggregator scores
2. **NIS-First Pricing** - All amounts in NIS, secondary currency in parentheses
3. **Route Comparison** - Always check nearby airports before booking direct
4. **3 Budget Tiers** - Present Budget / Mid-Range / Premium options
5. **Direct Booking** - Check hotel direct sites for savings vs Booking.com
6. **Be Realistic** - Don't over-schedule; allow for rest and spontaneity
7. **Book Ahead** - Popular attractions sell out, especially in peak season
8. **Cultural Respect** - Research and follow local customs
9. **Safety First** - Check travel advisories, register with embassy

## Technical Notes

**Data Storage:**
- Preferences: `~/.claude/travel_planner/preferences.json`
- Trips: `~/.claude/travel_planner/trips.json`

**CLI Commands:**
```bash
# Check initialization
python3 scripts/travel_db.py is_initialized

# View data
python3 scripts/travel_db.py get_preferences
python3 scripts/travel_db.py get_trips current
python3 scripts/travel_db.py stats

# Generate plan
python3 scripts/plan_generator.py --trip-id <id> --output plan.json

# Export backup
python3 scripts/travel_db.py export > backup.json
```

## Resources

### scripts/travel_db.py
Database management for preferences, trips, budget tracking, itineraries, and travel statistics. Stores routes, budget tiers, and currency data alongside trip info.

### scripts/plan_generator.py
Generates itineraries, multi-tier budgets, route comparison tables, forum-first hotel entries, car rental sections, driving routes, packing checklists, and preparation timelines. Includes `filter_forum_quotes()` for enforcing recency guardrails on forum data.

### references/travel_guidelines.md
Comprehensive guide for destination research, budget planning, itinerary creation, packing strategies, and safety tips.

### references/cultural_etiquette.md
Templates and guidelines for researching country-specific customs, dress codes, dining etiquette, religious considerations, and common mistakes to avoid.

### references/report_template.md
Full markdown template for the Smart Route Optimizer report format with route comparison, per-route sections, budget tiers, and booking tips.