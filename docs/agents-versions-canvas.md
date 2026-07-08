# Agents Versions Canvas

Weekly **Agents Versions** dashboard for `guestyorg/1000-agents-hub-workflows`, using `git log --follow` per `specs/core/use-cases/<agent>/` folder.

## Quick start (recommended)

Open **`1000-agents-hub-workflows`** in Cursor, then run:

```bash
./scripts/refresh_agents_versions_canvas.sh
```

Or paste Rami's prompt in Agent mode — it will pull `master`, compute stats, and write **Agents Versions** canvas.

## What the canvas shows

| Section | Content |
|--------|---------|
| Headline stats | Total agents, folder-scoped commits, avg commits/agent, scaffolded count (0 commits) |
| Left donut | Activity tiers: Bootstrap (1), Early (2–4), Active (5–9), Mature (10+) |
| Right | Weekly commit velocity (ISO weeks) + top 6 agents with commit counts and authors |

Scaffolded = agent folder exists but has **no** folder-scoped commits yet.

## Scripts in this repo

If you keep the tooling in `PRD-Cross-Project` instead:

```bash
# Clone/pull into vendor/ and refresh canvas
./scripts/refresh_agents_versions_canvas.sh

# Or point at an existing local clone
AGENTS_VERSIONS_REPO=~/code/1000-agents-hub-workflows ./scripts/refresh_agents_versions_canvas.sh
```

Outputs:

- `exports/agents_versions.json` — data snapshot
- `~/.cursor/projects/<workspace-slug>/canvases/Agents Versions.canvas.tsx` — Cursor Canvas

## Requirements

- Git access to `guestyorg/1000-agents-hub-workflows` (Guesty GitHub org)
- Cursor 3.1+ with Canvas support

## Weekly refresh

Re-run the refresh script (or the Agent prompt) each week before status. No E2E section, numbered-slots notes, long insights block, or full agent table on the summary.
