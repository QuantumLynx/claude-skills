# QuantumLynx Plugins

Claude Code plugins for travel planning and linter-driven development.

## Plugins

- **travel-planner** — Travel planning assistant with route discovery, forum-first reviews, and multi-tier budgets
- **go-linter-driven-development** — Linter-driven development workflow for Go
- **ts-react-linter-driven-development** — Linter-driven development workflow for TypeScript + React

## Installation

```bash
# Add the marketplace repository
/plugin marketplace add QuantumLynx/claude-skills

# Install individual plugins
/plugin install travel-planner@quantumlynx-skills
/plugin install go-linter-driven-development@quantumlynx-skills
/plugin install ts-react-linter-driven-development@quantumlynx-skills
```

## Usage

Once installed, skills activate automatically based on your task context. You can also invoke them directly:

```bash
# List available skills from installed plugins
/skills
```
