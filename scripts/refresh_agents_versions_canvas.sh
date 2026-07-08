#!/usr/bin/env bash
# Pull latest master from 1000-agents-hub-workflows and refresh the Agents Versions canvas.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXTRA_ARGS=()

if [[ -d "$ROOT/specs/core/use-cases" ]]; then
  REPO="$ROOT"
  BRANCH="${AGENTS_VERSIONS_BRANCH:-master}"
  echo "Detected workflows repo at $REPO — pulling origin/$BRANCH..."
  git -C "$REPO" fetch origin "$BRANCH"
  git -C "$REPO" checkout "$BRANCH"
  git -C "$REPO" pull --ff-only origin "$BRANCH"
  EXTRA_ARGS+=(--skip-git)
else
  REPO="${AGENTS_VERSIONS_REPO:-$ROOT/vendor/1000-agents-hub-workflows}"
  BRANCH="${AGENTS_VERSIONS_BRANCH:-master}"
fi

JSON_OUT="${AGENTS_VERSIONS_JSON:-$ROOT/exports/agents_versions.json}"
CANVAS_OUT="${AGENTS_VERSIONS_CANVAS:-$HOME/.cursor/projects/workspace/canvases/Agents Versions.canvas.tsx}"

exec python3 "$ROOT/scripts/build_agents_versions.py" \
  --repo "$REPO" \
  --branch "$BRANCH" \
  --json-out "$JSON_OUT" \
  --canvas-out "$CANVAS_OUT" \
  "${EXTRA_ARGS[@]}" \
  "$@"
