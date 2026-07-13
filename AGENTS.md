# AGENTS.md

Guidance for AI agents working in this repository.

## Project overview

**PRD-Cross-Project** is a placeholder repository (name suggests cross-project product requirements / documentation). As of the initial commit, it contains only `README.md` — no application source, dependency manifests, Docker setup, or CI configuration.

When application code or infrastructure is added, update this file with concrete install, lint, test, and run commands.

## Cursor Cloud specific instructions

- **Scope:** There is nothing to install beyond cloning the repo. The VM update script is a no-op (`true`).
- **Services:** No services are defined. Do not expect databases, APIs, or frontends until they are added to the repo.
- **Lint / test / build:** Not applicable until tooling (e.g. `package.json`, `Makefile`, `.github/workflows`) exists.
- **Running “the app”:** Not applicable. To sanity-check the VM, you can serve static files from the repo root, e.g. `python3 -m http.server 8765` and open or `curl` `http://127.0.0.1:8765/README.md`.
- **VM tooling (typical Cloud Agent image):** Git, Node.js (via nvm, ~v22), npm/pnpm/yarn, Python 3.12. Docker is not assumed to be installed unless added later.
- **Git:** Single branch `main`; remote `origin` on GitHub (`maiagordon-commits/PRD-Cross-Project`).

## Suggested workflow once code exists

1. Read the root `README.md` and any new setup docs.
2. Install dependencies per the stack added (npm/pnpm, pip, etc.).
3. Document required services and ports in this section.
4. Run lint and tests before commits, per project conventions.
