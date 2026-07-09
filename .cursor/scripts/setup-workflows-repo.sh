#!/usr/bin/env bash
# Clone or update guestyorg/1000-agents-hub-workflows for cloud-agent multi-repo access.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REPO_DIR="${AGENTS_VERSIONS_REPO:-$ROOT/vendor/1000-agents-hub-workflows}"
BRANCH="${AGENTS_VERSIONS_BRANCH:-master}"
REMOTE_URL="${AGENTS_VERSIONS_REMOTE:-https://github.com/guestyorg/1000-agents-hub-workflows.git}"

mkdir -p "$(dirname "$REPO_DIR")"

if [[ -d "$REPO_DIR/.git" ]]; then
  echo "Updating workflows repo at $REPO_DIR"
  git -C "$REPO_DIR" fetch origin "$BRANCH"
  git -C "$REPO_DIR" checkout "$BRANCH"
  git -C "$REPO_DIR" pull --ff-only origin "$BRANCH"
else
  echo "Cloning workflows repo into $REPO_DIR"
  git clone --depth 1 -b "$BRANCH" "$REMOTE_URL" "$REPO_DIR"
fi

echo "Workflows repo ready at $REPO_DIR ($(git -C "$REPO_DIR" rev-parse --short HEAD))"
