#!/usr/bin/env python3
"""Build Agents Versions dashboard data from 1000-agents-hub-workflows git history.

Uses `git log --follow` per agent folder under specs/core/use-cases/.

Usage:
    python3 scripts/build_agents_versions.py [--repo PATH] [--branch master]
        [--json-out PATH] [--canvas-out PATH]

Environment:
    AGENTS_VERSIONS_REPO  default repo path (cloned/pulled if missing)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_REPO = Path(__file__).resolve().parents[1] / "vendor" / "1000-agents-hub-workflows"
USE_CASES_ROOT = Path("specs/core/use-cases")
AGENT_DIR_RE = re.compile(r"^\d{2}-[a-z0-9-]+$")
ISO_WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")


def detect_repo_path(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    env = os.environ.get("AGENTS_VERSIONS_REPO")
    if env:
        return Path(env)
    cwd = Path.cwd()
    if (cwd / USE_CASES_ROOT).is_dir():
        return cwd
    return DEFAULT_REPO


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    date: str  # YYYY-MM-DD


def run(cmd: list[str], *, cwd: Path) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}"
        )
    return proc.stdout


def ensure_repo(repo: Path, branch: str, remote_url: str) -> None:
    if repo.exists() and (repo / ".git").exists():
        run(["git", "fetch", "origin", branch], cwd=repo)
        run(["git", "checkout", branch], cwd=repo)
        run(["git", "pull", "--ff-only", "origin", branch], cwd=repo)
        return

    repo.parent.mkdir(parents=True, exist_ok=True)
    run(
        ["git", "clone", "--depth", "1", "--branch", branch, remote_url, str(repo)],
        cwd=repo.parent,
    )


def list_agent_dirs(repo: Path) -> list[str]:
    root = repo / USE_CASES_ROOT
    if not root.is_dir():
        raise SystemExit(f"Missing use-cases root: {root}")
    return sorted(
        p.name for p in root.iterdir() if p.is_dir() and AGENT_DIR_RE.match(p.name)
    )


def folder_commits(repo: Path, agent: str) -> list[Commit]:
    folder = USE_CASES_ROOT / agent
    out = run(
        [
            "git",
            "log",
            "--follow",
            "--format=%H\t%an\t%ad",
            "--date=short",
            "--",
            str(folder),
        ],
        cwd=repo,
    )
    commits: list[Commit] = []
    seen: set[str] = set()
    for line in out.splitlines():
        if not line.strip():
            continue
        sha, author, date = line.split("\t", 2)
        if sha in seen:
            continue
        seen.add(sha)
        commits.append(Commit(sha=sha, author=author, date=date))
    return commits


def tier_for(count: int) -> str | None:
    if count == 0:
        return None
    if count == 1:
        return "Bootstrap"
    if 2 <= count <= 4:
        return "Early"
    if 5 <= count <= 9:
        return "Active"
    return "Mature"


def iso_week_label(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def sort_weeks(weeks: list[str]) -> list[str]:
    def key(label: str) -> tuple[int, int]:
        m = ISO_WEEK_RE.match(label)
        if not m:
            return (0, 0)
        return (int(m.group(1)), int(m.group(2)))

    return sorted(weeks, key=key)


def build_model(repo: Path, branch: str) -> dict[str, Any]:
    agents = list_agent_dirs(repo)
    per_agent: dict[str, list[Commit]] = {}
    all_commits: list[tuple[str, Commit]] = []

    for agent in agents:
        commits = folder_commits(repo, agent)
        per_agent[agent] = commits
        for c in commits:
            all_commits.append((agent, c))

    counts = {agent: len(per_agent[agent]) for agent in agents}
    total_agents = len(agents)
    folder_scoped_commits = len({c.sha for _, c in all_commits})
    scaffolded_count = sum(1 for n in counts.values() if n == 0)
    avg_commits = round(folder_scoped_commits / total_agents, 1) if total_agents else 0.0

    tier_labels = ["Bootstrap", "Early", "Active", "Mature"]
    tier_counts = Counter(tier_for(n) for n in counts.values() if tier_for(n))
    activity_tiers = [
        {
            "tier": label,
            "label": {
                "Bootstrap": "Bootstrap (1)",
                "Early": "Early (2–4)",
                "Active": "Active (5–9)",
                "Mature": "Mature (10+)",
            }[label],
            "count": tier_counts.get(label, 0),
        }
        for label in tier_labels
    ]

    weekly = Counter(iso_week_label(c.date) for _, c in all_commits)
    week_labels = sort_weeks(list(weekly.keys()))
    if len(week_labels) > 12:
        week_labels = week_labels[-12:]
    weekly_velocity = [{"week": w, "commits": weekly[w]} for w in week_labels]

    ranked = sorted(
        (
            {
                "agent": agent,
                "commits": counts[agent],
                "authors": sorted({c.author for c in per_agent[agent]}),
            }
            for agent in agents
        ),
        key=lambda row: (-row["commits"], row["agent"]),
    )

    head_sha = run(["git", "rev-parse", "--short", "HEAD"], cwd=repo).strip()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return {
        "title": "Agents Versions",
        "repo": "guestyorg/1000-agents-hub-workflows",
        "branch": branch,
        "head": head_sha,
        "generatedAt": generated_at,
        "useCasesRoot": str(USE_CASES_ROOT),
        "stats": {
            "totalAgents": total_agents,
            "folderScopedCommits": folder_scoped_commits,
            "avgCommitsPerAgent": avg_commits,
            "scaffoldedCount": scaffolded_count,
        },
        "activityTiers": activity_tiers,
        "weeklyVelocity": weekly_velocity,
        "topAgents": ranked[:6],
    }


def render_canvas(model: dict[str, Any]) -> str:
    state_literal = json.dumps(model, indent=2)
    return f"""/* AUTO-GENERATED by scripts/build_agents_versions.py */
import {{
  Card,
  CardBody,
  CardHeader,
  Grid,
  H1,
  H2,
  LineChart,
  PieChart,
  Stack,
  Stat,
  Table,
  Text,
  useHostTheme,
}} from 'cursor/canvas';

interface TopAgentRow {{
  agent: string;
  commits: number;
  authors: string[];
}}

interface AgentsVersionsModel {{
  title: string;
  repo: string;
  branch: string;
  head: string;
  generatedAt: string;
  useCasesRoot: string;
  stats: {{
    totalAgents: number;
    folderScopedCommits: number;
    avgCommitsPerAgent: number;
    scaffoldedCount: number;
  }};
  activityTiers: Array<{{ tier: string; label: string; count: number }}>;
  weeklyVelocity: Array<{{ week: string; commits: number }}>;
  topAgents: TopAgentRow[];
}}

const DATA: AgentsVersionsModel = {state_literal};

function formatAuthors(authors: string[]): string {{
  if (!authors.length) return '—';
  if (authors.length <= 2) return authors.join(', ');
  return `${{authors.slice(0, 2).join(', ')}} +${{authors.length - 2}}`;
}}

export default function AgentsVersions(): JSX.Element {{
  useHostTheme();
  const {{ stats, activityTiers, weeklyVelocity, topAgents }} = DATA;

  const tierChart = activityTiers.map((t) => ({{
    label: t.label,
    value: t.count,
  }}));

  const velocityChart = weeklyVelocity.map((w) => ({{
    x: w.week,
    y: w.commits,
  }}));

  const topRows = topAgents.map((row) => ({{
    agent: row.agent,
    commits: String(row.commits),
    authors: formatAuthors(row.authors),
  }}));

  return (
    <Stack gap={{16}}>
      <Stack gap={{4}}>
        <H1>{{DATA.title}}</H1>
        <Text tone="secondary">
          {{DATA.repo}} @ {{DATA.branch}} ({{DATA.head}}) · git log --follow per {{DATA.useCasesRoot}}/
          folder · weekly buckets · {{DATA.generatedAt}}
        </Text>
      </Stack>

      <Grid columns={{4}} gap={{12}}>
        <Stat label="Total agents" value={{String(stats.totalAgents)}} />
        <Stat label="Folder-scoped commits" value={{String(stats.folderScopedCommits)}} />
        <Stat label="Avg commits / agent" value={{String(stats.avgCommitsPerAgent)}} />
        <Stat label="Scaffolded" value={{String(stats.scaffoldedCount)}} />
      </Grid>

      <Grid columns={{2}} gap={{16}}>
        <Card>
          <CardHeader>
            <H2>Activity tiers</H2>
          </CardHeader>
          <CardBody>
            <PieChart data={{tierChart}} variant="donut" height={{280}} />
          </CardBody>
        </Card>

        <Stack gap={{16}}>
          <Card>
            <CardHeader>
              <H2>Weekly commit velocity</H2>
            </CardHeader>
            <CardBody>
              <LineChart
                data={{velocityChart}}
                xLabel="ISO week"
                yLabel="Commits"
                height={{220}}
              />
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <H2>Top 6 agents</H2>
            </CardHeader>
            <CardBody>
              <Table
                columns={{[
                  {{ key: 'agent', header: 'Agent', width: '42%' }},
                  {{ key: 'commits', header: 'Commits', width: '14%' }},
                  {{ key: 'authors', header: 'Authors', width: '44%' }},
                ]}}
                rows={{topRows}}
              />
            </CardBody>
          </Card>
        </Stack>
      </Grid>
    </Stack>
  );
}}
"""


def default_canvas_path() -> Path:
    workspace = Path(__file__).resolve().parents[1]
    slug = str(workspace.resolve()).lstrip("/").replace("/", "-")
    return Path.home() / ".cursor" / "projects" / slug / "canvases" / "Agents Versions.canvas.tsx"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=None)
    parser.add_argument("--branch", default="master")
    parser.add_argument(
        "--remote-url",
        default="https://github.com/guestyorg/1000-agents-hub-workflows.git",
    )
    parser.add_argument("--json-out", type=Path, default=Path("exports/agents_versions.json"))
    parser.add_argument("--canvas-out", type=Path, default=default_canvas_path())
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Use existing repo checkout without fetch/pull",
    )
    args = parser.parse_args()
    repo = detect_repo_path(args.repo)

    if not args.skip_git:
        ensure_repo(repo, args.branch, args.remote_url)

    model = build_model(repo, args.branch)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")

    args.canvas_out.parent.mkdir(parents=True, exist_ok=True)
    args.canvas_out.write_text(render_canvas(model), encoding="utf-8")

    print(f"Wrote {args.json_out}")
    print(f"Wrote {args.canvas_out}")
    print(
        "Summary: "
        f"{model['stats']['totalAgents']} agents, "
        f"{model['stats']['folderScopedCommits']} commits, "
        f"{model['stats']['scaffoldedCount']} scaffolded"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
