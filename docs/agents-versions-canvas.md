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

## Cloud Agents setup (weekly automation)

This repo includes `.cursor/environment.json` so Cloud Agents can access the workflows repo.

### One-time dashboard steps (you)

1. **GitHub integration** — [Cursor Integrations](https://cursor.com/dashboard/integrations) → GitHub → ensure Guesty org is connected and the Cursor GitHub App can access `guestyorg/1000-agents-hub-workflows`. If the repo is missing, ask a Guesty GitHub org admin to grant the Cursor app access to that repository.

2. **Add the dependency repo to your environment** — open your environment settings:
   [PRD-Cross-Project Cloud Environment](https://cursor.com/dashboard/cloud-agents/environments/r/github.com/maiagordon-commits/prd-cross-project)
   - Click **Edit** / **Add repository**
   - Add `github.com/guestyorg/1000-agents-hub-workflows` on branch `master`
   - Save and let setup re-run (or start a new cloud agent from a branch that includes `.cursor/environment.json`)

3. **Merge** [PR #12](https://github.com/maiagordon-commits/PRD-Cross-Project/pull/12) (or the branch with `environment.json`) so the config is on `main`.

The committed config does two things:

- `repositoryDependencies` — expands the cloud agent GitHub token to include the workflows repo
- `install` — runs `.cursor/scripts/setup-workflows-repo.sh` to clone/update into `vendor/1000-agents-hub-workflows`

### Weekly cloud agent prompt

From a cloud agent on this repo (after setup above):

```
Pull latest master from 1000-agents-hub-workflows. Build a Cursor Canvas called Agents Versions: 4 headline stats (total agents, folder-scoped commits, avg commits/agent, scaffolded count), left donut for activity tiers (Bootstrap 1 / Early 2–4 / Active 5–9 / Mature 10+), right side weekly commit velocity line chart + top 6 agents list with commits and authors. Use git log --follow per specs/core/use-cases/ folder. Weekly only. No E2E, no numbered-slots notes, no long insights block, no redundant full table on the summary.
```

Or run:

```bash
./scripts/refresh_agents_versions_canvas.sh
```

Then share the canvas from **Cursor → Canvases → Agents Versions → Share**.

## Requirements

- Git access to `guestyorg/1000-agents-hub-workflows` (Guesty GitHub org)
- Cursor 3.1+ with Canvas support

## Weekly refresh

Re-run the refresh script (or the Agent prompt) each week before status. No E2E section, numbered-slots notes, long insights block, or full agent table on the summary.
