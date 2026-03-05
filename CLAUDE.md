# QuantumLynx Skills

Claude Code skills plugin following the [Anthropic skills](https://github.com/anthropics/skills) format.

## Installation

```bash
/plugin marketplace add QuantumLynx/skills
/plugin install travel-planner@quantumlynx-skills
```

## Project Structure

```
.claude-plugin/marketplace.json  # Plugin registry
skills/
  travel-planner/
    SKILL.md                     # Skill instructions (source of truth)
    scripts/
      travel_db.py               # JSON-based preference/trip database
      plan_generator.py          # Budget, route, hotel, car formatters
    references/
      cultural_etiquette.md      # Cultural guidelines template
      travel_guidelines.md       # General travel planning guide
      report_template.md         # Smart route optimizer report template
tests/                           # pytest test suite
docs/design/                     # Design documents and plans
```

## Tech Stack

- Python 3 (scripts)
- JSON file storage (~/.claude/travel_planner/)
- Claude Code skills framework
- WebSearch/WebFetch (used by Claude at plan time)

## Running Tests

```bash
python3 -m pytest tests/ -v
```

# currentDate
Today's date is 2026-03-05.
