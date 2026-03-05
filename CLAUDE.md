# QuantumLynx Plugins

Multi-plugin Claude Code repository following the [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) format.

## Installation

```bash
/plugin marketplace add QuantumLynx/claude-tutor
/plugin install travel-planner@quantumlynx-skills
/plugin install go-linter-driven-development@quantumlynx-skills
/plugin install ts-react-linter-driven-development@quantumlynx-skills
```

## Project Structure

```
.claude-plugin/marketplace.json        # Root plugin registry
plugins/
  travel-planner/
    .claude-plugin/plugin.json         # Plugin metadata
    skills/
      travel-planner/
        SKILL.md                       # Skill instructions (source of truth)
        scripts/
          travel_db.py                 # JSON-based preference/trip database
          plan_generator.py            # Budget, route, hotel, car formatters
        references/
          cultural_etiquette.md        # Cultural guidelines template
          travel_guidelines.md         # General travel planning guide
          report_template.md           # Smart route optimizer report template
  go-linter-driven-development/
    .claude-plugin/plugin.json         # Plugin metadata
    skills/                            # 6 specialized skills
    agents/                            # Quality analyzer, code reviewer
    commands/                          # LDD workflow commands
  ts-react-linter-driven-development/
    .claude-plugin/plugin.json         # Plugin metadata
    skills/                            # 6 specialized skills
tests/                                 # pytest test suite
docs/design/                           # Design documents and plans
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
