---
name: travel-planner
description: Use when planning trips, creating travel itineraries, managing travel budgets, or seeking destination advice. Covers single-city vacations, multi-city road trips, and open-jaw flight routing. Handles family travel, solo trips, and group planning.
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
1. **Destination**: City/country (or multiple regions for road trips)
2. **Dates**: Departure and return dates (or flexible date range)
3. **Duration**: Number of days
4. **Budget**: Total budget or daily budget
5. **Purpose**: Vacation, business, special occasion
6. **Must-see/do**: Specific attractions or activities
7. **Origin**: Home airport/city (do NOT assume TLV — ask if not stated)
8. **Trip type**: Single-city, multi-city, or road trip

**Detect trip type** from user input:
- Single destination → standard workflow (Steps 4-7)
- Multiple cities/regions → multi-destination workflow (adds Step 4b, per-region accommodation in Step 7)

**Creating Trip (single destination):**

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

**Creating Trip (multi-destination / road trip):**

```python
from travel_db import add_trip

trip = {
    "destination": {
        "country": "Italy",
        "segments": [
            {"region": "Dolomites", "nights": 5, "transport": "rental car", "accommodation_type": "hotel"},
            {"region": "Tuscany", "nights": 4, "transport": "rental car", "accommodation_type": "agriturismo"},
            {"region": "Florence", "nights": 2, "transport": "on foot", "accommodation_type": "hotel"},
            {"region": "Rome", "nights": 2, "transport": "on foot", "accommodation_type": "hotel"}
        ]
    },
    "transport_modes": {
        "car_rental": {"pickup": "VCE", "dropoff": "Florence", "days": 11},
        "trains": [{"from": "Florence", "to": "Rome", "type": "high-speed"}]
    },
    "flights": {
        "inbound": {"from": "TLV", "to": "VCE"},
        "outbound": {"from": "FCO", "to": "TLV"}
    },
    "departure_date": "2026-07-11",
    "return_date": "2026-07-24",
    "duration_days": 14,
    "budget": {"total": 0, "currency": "NIS"},
    "purpose": "family vacation",
    "travelers": 4,
    "climate": "warm Mediterranean / alpine",
    "activities": ["hiking", "sightseeing", "food", "culture"]
}

trip_id = add_trip(trip, status="current")
```

### Step 4: Alternative Route Discovery

Before researching the destination in depth, search for alternative travel routes.
The goal: find cheaper or more convenient ways to reach the destination.

**First: Identify flight pattern from trip type:**
- **Round-trip (single destination)**: Same airport in/out → search round-trip flights
- **Open-jaw (road trip / multi-city)**: Fly into airport A near trip START, out of airport B near trip END → search each leg separately. This is very common for road trips and often cheaper than backtracking.

**Process (parameterize {origin} from user's home airport — do NOT hardcode TLV):**
1. WebSearch: "airports within 500km of {first destination}" (for arrival airport candidates)
2. For open-jaw: WebSearch: "airports within 200km of {last destination}" (for departure airport candidates)
3. WebSearch: "cheapest flights from {origin_airport} to {arrival_airport} {month} {year}"
4. WebSearch: "{LCC carriers from origin} {origin_code} to {country} {month} {year}"
5. WebSearch: "{nearby airport} to {destination} transport options car train"
6. For open-jaw: WebSearch: "cheapest flights from {departure_airport} to {origin_airport} {month} {year}"

**Open-Jaw Strategy (fly into A, out of B):**
Compare arrival airports by proximity to FIRST destination AND departure airports by proximity to LAST destination. Example for Italy road trip starting in Dolomites, ending in Rome:
- **Arrival**: Venice (VCE) 2h to Dolomites vs Milan (MXP) 3.5h — Venice wins
- **Departure**: Rome (FCO) — obvious choice, trip ends there
- Open-jaw VCE+FCO often costs similar to round-trip to either city

**LCC Carrier Strategy:**
- Research which LCC carriers serve the origin airport (e.g., Wizz Air, Ryanair, EasyJet, etc.)
- Always calculate total cost WITH checked bag (22kg) — LCC "base fare" is misleading
- Check secondary airports (e.g., Milan BGY vs MXP, Rome CIA vs FCO)

For each candidate route (max 4), estimate:
- Flight cost from origin (in user's home currency) — include checked bag for LCC
- Ground transport cost + time to first/last destination
- Total cost comparison

**Example for Salzburg, Austria (from TLV):**
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

### Step 4b: Multi-Destination Transport Planning (Road Trips Only)

Skip this step for single-destination trips. For multi-region road trips:

**Car Rental Logistics:**
- Identify pickup airport and drop-off location (check one-way fee — same country usually free or low)
- Calculate total rental days (only for car segments, not city-only segments)
- Research ZTL / restricted traffic zones for each city on route — list them in the plan with specific warnings
- Estimate fuel + toll costs per segment
- Vehicle size: match to group size + luggage for FULL trip duration (not just car segments)

**Mixed Transport Planning:**
- Identify where to drop the car (train station? airport? city edge?)
- Research train options between segments (high-speed vs regional, booking sites)
- Check family discounts (e.g., Italo: children under 14 ride free with paying adult)
- Plan car return + train departure on same day with 2h+ buffer
- Research intercity transport apps (Trenitalia, Italo, SNCF, DB Navigator, etc.)

**Key Distances Table:**
Generate a distances/drive-times table for ALL inter-segment drives. Include:
- Distance in km
- Estimated drive time
- Highway names / route
- Scenic alternatives with time penalty
- Notable stops or rest areas

**Driving Warnings Section:**
Research and compile per-country:
- Restricted traffic zones (ZTL in Italy, LEZ in Germany/Netherlands, etc.)
- Toll systems (autostrada cards, vignettes, electronic tolls)
- Speed enforcement (fixed cameras, average speed cameras)
- Required equipment (reflective vest, warning triangle, breathalyzer in France)
- Child seat laws by age/height
- IDP requirements

### Step 5: Review-Based Search (Hotels & Car Rentals)

For each viable route, search for hotels and car rentals using FORUM-FIRST approach.

**Review Source Priority (forums first, aggregators second):**
1. Origin-country travel forums (e.g., FlyTalk.co.il/Lametayel.co.il for Israeli travelers, MoneySavingExpert for UK, Routard for French, etc.)
2. Reddit (r/travel, r/solotravel, r/TravelHacks, origin-specific subs, destination subs)
3. Travel forums (Lonely Planet Thorn Tree, FlyerTalk, TripAdvisor forum posts)
4. Google Maps reviews (local voices, recent experiences)
5. TripAdvisor/Booking.com scores (secondary data point only)

**Forum Guardrails — MANDATORY:**
- **Recency**: Only use quotes from the last 24 months. Use `filter_forum_quotes()` from `plan_generator.py` to enforce.
- **Triangulation**: A claim needs 3+ independent sources to be presented as fact. Single-source opinions must be attributed ("one Redditor says...").
- **Credibility scoring**: Prefer posts with high upvotes/engagement. Flag accounts with no history.

**Hotel Search:**

Search queries (adapt forum sites to user's origin country):
- `site:{origin_country_forum} "{destination}" hotel` (origin-country forum in local language)
- `site:reddit.com "{destination}" hotel recommendation`
- `site:reddit.com "{destination}" where to stay`
- `"{destination}" best hotel review site:tripadvisor.com/ShowTopic`
- `"{destination}" hotels near {target area} site:booking.com`
- Check hotel direct websites for lower prices

Selection criteria (in order):
1. **Proximity to target** (weighted highest) - walking distance to main area
2. **Forum sentiment** - real quotes from Reddit/forums
3. **Review scores** - Booking.com 8.5+, Google Maps 4.3+, TripAdvisor 4.0+

Find 2-3 hotels per budget tier (adjust ranges to destination and traveler's currency):
- Budget: low-cost options (hostels, basic hotels, budget Airbnb)
- Mid-Range: comfortable hotels, well-reviewed Airbnb
- Premium: luxury hotels, high-end boutique properties

Also search for 1 Airbnb alternative per tier.

**Car Rental Search:**

Search queries (adapt forum sites to user's origin country):
- `site:{origin_country_forum} "{airport/city}" car rental` (origin-country forum in local language)
- `site:reddit.com "{airport/city}" car rental recommendation`
- `site:reddit.com "{airport/city}" rent car avoid`
- `"{city}" car rental google maps reviews`

Preference: local companies with Google Maps 4.5+ over international chains.
Include: daily rate, insurance notes (CDW/SCDW coverage, excess amounts), pickup/dropoff, customer complaints.

**Insurance Notes:**
- CDW (Collision Damage Waiver) is essential — verify excess amount (typically EUR 800-1500)
- SCDW (Super CDW) reduces excess to zero — often worth the extra cost per day
- Check if traveler's home credit card provides rental car insurance (many premium cards do)
- IDP (International Driving Permit) required in some countries — check before departure based on traveler's license country

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

**Report structure (single-destination):**

1. **Route Comparison Table** - Use `format_route_comparison_table()` at the top
2. **Per-Route Sections** - For each viable route:
   - Flights table (airline, route, price/pp, with bag, departure)
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

**Additional sections for multi-destination / road trips:**

1. **Route Overview Table** - Segment | Nights | Transport | Highlights (at the very top)
2. **Flights Section** - Separate tables for inbound and outbound legs (open-jaw)
3. **Car Rental Section** - Pickup/drop-off locations, one-way fee, vehicle size for group
4. **Per-Region Accommodation** - Separate hotel/accommodation section per segment/region, since costs and styles vary dramatically (e.g., mountain hotel vs agriturismo vs city hotel)
5. **Key Distances & Drive Times Table** - All inter-segment driving distances, times, roads, and scenic alternatives
6. **Driving Warnings** - ZTL zones, toll systems, speed limits, required equipment, child seat laws
7. **Mixed Transport Section** - Car drop-off logistics, train bookings, family discounts, city transport
8. **Day-by-Day Itinerary** - Must include driving days as dedicated entries with stops, distances, and realistic arrival times
9. **Budget Breakdown by Tier** - Use `calculate_multi_region_budget()` for per-segment accommodation costs:

```python
from plan_generator import calculate_multi_region_budget

tiers = calculate_multi_region_budget(
    segments=[
        {"region_name": "Dolomites", "nights": 5, "accommodation_multiplier": 1.3},
        {"region_name": "Tuscany", "nights": 4, "accommodation_multiplier": 0.9},
        {"region_name": "Florence", "nights": 2, "accommodation_multiplier": 1.1},
        {"region_name": "Rome", "nights": 2, "accommodation_multiplier": 1.0},
    ],
    num_travelers=4,
    destination_region="europe"
)
```

**Pricing rules:**
- All prices in user's home currency first, destination currency in parentheses
- Show per-person AND total amounts
- Include rate date for currency conversions

**Itinerary rules:**
- Based on recommended route
- Logical geographic grouping
- Realistic timing with buffers (especially on driving/transit days)
- Mix of activity types
- Meal suggestions with local prices
- Transportation details between activities
- Driving days: include distance, time, suggested stops, and arrival time estimates

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
2. **Home-Currency-First Pricing** - All amounts in traveler's home currency first, destination currency in parentheses
3. **Route Comparison** - Always check nearby airports before booking direct. For road trips, check open-jaw flights (fly into A, out of B)
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