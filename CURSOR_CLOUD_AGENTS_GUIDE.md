# Cursor Cloud Agents: Step-by-Step Creation Guide

This guide walks you through everything you need to know to create and configure Cursor Cloud Agents for your team.

---

## Table of Contents

1. [What Are Cloud Agents?](#what-are-cloud-agents)
2. [Prerequisites](#prerequisites)
3. [Step 1: Connect Source Control](#step-1-connect-source-control)
4. [Step 2: Create a Development Environment](#step-2-create-a-development-environment)
5. [Step 3: Configure Secrets and Environment Variables](#step-3-configure-secrets-and-environment-variables)
6. [Step 4: Launch Your First Cloud Agent](#step-4-launch-your-first-cloud-agent)
7. [Step 5: Using Cloud Agents from Different Surfaces](#step-5-using-cloud-agents-from-different-surfaces)
8. [Advanced Configuration](#advanced-configuration)
9. [Multi-Repo Environments](#multi-repo-environments)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

**Appendix: Guesty Agent-Hub Development**
- [A1. Where Things Live](#a1-where-things-live-important---changed-mid-flight)
- [A2. Environment Prerequisites](#a2-environment-prerequisites-one-time-setup)
- [A3. Author the Use Case](#a3-author-the-use-case)
- [A4. The 3 Mandatory Capabilities](#a4-the-3-mandatory-capabilities-no-prod-without-these)
- [A5. Validate + Run Locally](#a5-validate--run-locally-staging13-default-account)
- [A6. validation.json](#a6-validationjson-quality-gate)
- [A7. PR to the Registry](#a7-pr-to-the-registry)
- [A8. Deploy + Backoffice + Status](#a8-deploy--backoffice--status)
- [A9. Known Blockers & Fixes](#a9-known-blockers--fixes)
- [A10. Content, Copy & Help Center](#a10-content-copy--help-center-product-facing--dont-skip)
- [A11. Monitoring & Rollout](#a11-monitoring--rollout)
- [A12. Agent Design Pitfalls](#a12-agent-design-pitfalls-from-the-channel)
- [A13. Reference Links](#a13-reference-links)

---

## What Are Cloud Agents?

Cloud Agents are AI-powered development assistants that run in isolated virtual machines (VMs) in the cloud. Unlike local agents that run on your machine, Cloud Agents:

- Run in their own Ubuntu-based development environment
- Can build, test, and verify code changes autonomously
- Work in parallel without consuming local machine resources
- Can access MCP servers, databases, APIs, and third-party services
- Produce artifacts like screenshots, videos, and logs to demonstrate their work
- Create merge-ready pull requests when they complete tasks

**Key Benefits:**
- Run multiple agents simultaneously
- No need for your local machine to be connected
- Full development environment access (not just code editing)
- Can test and verify work before creating PRs

---

## Prerequisites

Before you can create and use Cloud Agents, ensure you have:

| Requirement | Details |
|-------------|---------|
| **Cursor Plan** | Pro plan ($20/month) or higher |
| **Usage-Based Billing** | Enabled with at least a $10 spending limit |
| **Privacy Mode** | Must be disabled (Cloud VMs need to receive your code) |
| **Source Control** | GitHub, GitLab, Azure DevOps, or Bitbucket Cloud connected with read-write permissions |

---

## Step 1: Connect Source Control

A Cursor account admin must connect source control before anyone can start cloud agents.

### For GitHub:

1. Go to [Cursor Integrations](https://www.cursor.com/dashboard/integrations)
2. Click **Connect** next to GitHub
3. Authorize Cursor to access your repositories
4. Select the repositories you want to use with Cloud Agents
5. Ensure you have read-write permissions to the repos

### For Other Providers:

- **GitLab (Cloud and Self-Hosted)**: Same process through Integrations dashboard
- **Bitbucket Cloud**: Connect via Integrations dashboard
- **Azure DevOps**: Connect via Integrations dashboard

**Important:** You need read-write privileges to your repo and any dependent repos or submodules.

---

## Step 2: Create a Development Environment

Environment setup is the **most important step** for effective Cloud Agents. An agent without a proper environment is like an engineer without a computer.

### Navigate to Cloud Agents Dashboard

Go to [Cloud Agents Dashboard](https://cursor.com/dashboard/cloud-agents#environments)

### Choose Your Setup Method

#### Option A: Agent-Driven Setup (Recommended)

This is the easiest approach and takes about 10 minutes:

1. Click **Create New Environment** in the dashboard
2. Connect your GitHub/GitLab/Azure DevOps/Bitbucket account
3. Select one or more repositories
4. Provide environment variables and secrets needed to install dependencies
5. Watch the agent set up the environment in a shared terminal session
6. Once Cursor verifies the code is working, **save a snapshot** of the VM
7. Commit the configuration to `.cursor/environment.json` so your team benefits

#### Option B: Manual Dockerfile Setup (Advanced)

For more control, configure with a Dockerfile:

1. Create a `.cursor/` directory in your repository root
2. Create a `Dockerfile` inside `.cursor/`
3. Create `.cursor/environment.json` with your configuration:

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "install": "npm install"
}
```

**Dockerfile Guidelines:**
- Install system-level dependencies, compilers, debuggers
- Do NOT `COPY` the full project (Cursor manages the workspace)
- Use build secrets for private package registries

### Environment Resolution Order

Cursor resolves environment configuration using the first match:

1. `.cursor/environment.json` in the repository
2. A personal saved environment
3. A team saved environment

---

## Step 3: Configure Secrets and Environment Variables

Cloud Agents need environment variables and secrets (API keys, database credentials) to run and test code.

### Add Secrets via Dashboard

1. Go to [Cloud Agents Dashboard](https://cursor.com/dashboard/cloud-agents)
2. Navigate to the **Secrets** tab
3. Add your secrets as key-value pairs

**Types of Secrets:**

| Type | Scope |
|------|-------|
| **User Secrets** | Available only to your agents |
| **Team Secrets** | Shared across team members |
| **Environment-Scoped** | Only available to agents using specific environments |

### Common Secrets to Add:

- `DATABASE_URL` - Database connection string
- `API_KEY` - External API keys
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `GITHUB_TOKEN` - For private package access
- Login credentials (username, email, password)
- TOTP secrets for 2FA (use `oathtool --totp -b "$TOTP_SECRET"` to generate codes)

### For Monorepos with Multiple .env Files:

- Add values from all `.env.local` files to the Secrets tab
- Use unique variable names when keys overlap (e.g., `NEXTJS_*`, `CONVEX_*`)

---

## Step 4: Launch Your First Cloud Agent

Once your environment is configured, you can launch a Cloud Agent.

### From Cursor Desktop:

1. Open Cursor IDE
2. Look at the agent input dropdown
3. Select **Cloud** instead of the default local mode
4. Type your task description
5. Press Enter to start the agent

### From Cursor Web:

1. Go to [cursor.com/agents](https://cursor.com/agents)
2. Select your repository
3. Type your task
4. Click to start the agent

### What Happens When an Agent Runs:

1. Cursor spins up an isolated Ubuntu VM
2. Clones your repository
3. Checks out a dedicated `agent/` branch from main
4. Runs your `install` command (e.g., `npm install`)
5. Starts any configured `start` commands
6. Works on your task autonomously
7. Tests and verifies changes
8. Opens a pull request when complete
9. Sends you a notification (email, desktop, or Slack)

---

## Step 5: Using Cloud Agents from Different Surfaces

Cloud Agents can be triggered from multiple interfaces:

### From Slack

1. Install the Cursor Slack app: [Installation Page](https://cursor.com/api/install-slack-app)
2. Mention `@cursor` with your prompt

**Commands:**
```
@Cursor [prompt]              # Start an agent or add follow-up
@Cursor settings              # Configure defaults
@Cursor agent [prompt]        # Force create a new agent in a thread
@Cursor list my agents        # Show running agents
@Cursor help                  # Get command list
```

**Options:**
```
@Cursor in acme/backend fix the login bug       # Specify repo
@Cursor with opus fix the bug                    # Specify model
@Cursor use the Platform environment update API  # Use named environment
@Cursor branch=dev fix the tests                 # Specify branch
```

### From GitHub/Bitbucket

Comment `@cursor` on any:
- GitHub Pull Request
- GitHub Issue
- Bitbucket Pull Request

### From Linear

Mention `@Cursor` on any Linear issue

### From iOS App

Download the [Cursor iOS app](https://cursor.com/docs/cloud-agent/mobile.md) to start and manage agents on the go

### Via API

Use the [Cloud Agent API](https://cursor.com/docs/cloud-agent/api/endpoints.md) for programmatic access

---

## Advanced Configuration

### The environment.json File

Create `.cursor/environment.json` for code-defined configuration:

**Using a snapshot:**
```json
{
  "snapshot": "snapshot-20260212-00000000-0000-0000-0000-000000000000",
  "install": "npm install"
}
```

**Using a Dockerfile:**
```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "install": "pnpm install && ./custom_script.sh"
}
```

### Update Commands

The `install` command runs when a new machine boots:

- Should be idempotent (safe to run multiple times)
- Common examples: `npm install`, `pip install -r requirements.txt`, `bazel build`
- Results are cached for faster subsequent starts

### Startup Commands

Configure processes that should stay alive while the agent runs:

```json
{
  "start": "sudo service docker start",
  "terminals": ["npm run dev", "npm run api"]
}
```

### AGENTS.md Instructions

Add cloud-specific instructions to your `AGENTS.md` file:

```markdown
## Cursor Cloud Specific Instructions

### Development Environment Setup
- Run `npm install` before starting any work
- Start the dev server with `npm run dev`

### Testing
- Run `npm test` to execute unit tests
- Run `npm run e2e` for end-to-end tests

### Deployment
- Use `npm run deploy:staging` for staging deployments
```

---

## Multi-Repo Environments

Use multi-repo environments when your agent needs to work across multiple repositories.

### When to Use:

- Frontend, backend, infrastructure in separate repos
- Shared libraries in their own repos
- Microservices architecture

### Setup:

1. Go to [Cloud Agents Dashboard](https://cursor.com/dashboard/cloud-agents#environments)
2. Create a new environment
3. Select **multiple repositories**
4. Configure which repos should be cloned and into which directories

### Benefits:

- Agent can inspect the full workspace
- Make coordinated changes across repos
- Run tests that span multiple repos
- Open pull requests in all affected repos

---

## Best Practices

### Environment Setup

- **Take snapshots** after successful setup - future agents start faster
- **Commit environment.json** to share with your team
- **Keep update scripts fast** - complex setup slows agent startup
- **Use AGENTS.md** for task-specific instructions agents can discover

### Secrets Management

- Store secrets in the dashboard, not in code
- Use environment-scoped secrets for staging vs. production
- Rotate credentials regularly
- Never commit `.env` files with real secrets

### Task Design

- Give clear, specific task descriptions
- Include success criteria when possible
- Break large tasks into smaller, focused requests
- Reference relevant files or documentation

### Team Collaboration

- Share agent URLs with teammates for visibility
- Enable [team follow-ups](https://cursor.com/docs/cloud-agent/settings.md#team-follow-ups) if needed
- Use channel settings in Slack for consistent defaults
- Set up routing rules for automatic repo/environment selection

---

## Troubleshooting

### Agent runs are not starting

- Ensure you're logged in to Cursor
- Verify your GitHub/GitLab/Azure DevOps/Bitbucket account is connected
- Check that you have necessary repository permissions
- Confirm you're on a paid Cursor plan with usage-based billing enabled

### Secrets aren't available to the agent

- Verify secrets are added in [Cloud Agents Dashboard](https://cursor.com/dashboard/cloud-agents)
- Secrets are workspace/team-scoped - ensure you're using the correct account
- Try restarting the cloud agent after adding new secrets

### Slack integration not working

- Verify workspace admin has installed the Cursor Slack app
- Check that you have proper permissions
- Run `@Cursor settings` to verify configuration

### Teammate can't open my agent

- Teammate must belong to the same Cursor team
- They need to connect their own source control account
- They need access to the repository the agent worked in

### Environment configuration issues

- Check for error messages in the agent view
- Verify your Dockerfile builds successfully locally
- Ensure all required secrets are configured
- Check that your update script is idempotent

---

## Quick Reference Card

| Action | How to Do It |
|--------|--------------|
| Create environment | [Dashboard](https://cursor.com/dashboard/cloud-agents#environments) → Create New |
| Add secrets | Dashboard → Secrets tab → Add secret |
| Start agent (Desktop) | Agent input → Select "Cloud" → Type task |
| Start agent (Web) | [cursor.com/agents](https://cursor.com/agents) |
| Start agent (Slack) | `@Cursor [your task]` |
| Start agent (GitHub) | Comment `@cursor` on PR/issue |
| View running agents | [cursor.com/agents](https://cursor.com/agents) or `@Cursor list my agents` |
| Configure Slack channel | `@Cursor settings` |

---

## Additional Resources

- [Cloud Agent Overview](https://cursor.com/docs/cloud-agent)
- [Cloud Agent Setup](https://cursor.com/docs/cloud-agent/setup.md)
- [Cloud Agent Capabilities](https://cursor.com/docs/cloud-agent/capabilities.md)
- [Cloud Agent Security](https://cursor.com/docs/cloud-agent/security-network.md)
- [Slack Integration](https://cursor.com/docs/integrations/slack)
- [Cloud Agent API](https://cursor.com/docs/cloud-agent/api/endpoints.md)

---

## Appendix: Guesty Agent-Hub Development Workflow

This section covers the internal workflow for building Guesty Agent-Hub agents end-to-end.

> **Golden path:** author from master → add the 3 mandatory capabilities → validate + run on staging13 → PR to `agent-workflow-registry` → copy + HC article → deploy + set status → monitor → roll out in stages.

---

### A1. Where Things Live (Important - Changed Mid-Flight)

- **Use-cases (workflows) no longer live in `1000-agents-hub-workflows`.** Source of truth is the separate repo **`guestyorg/agent-workflow-registry`**.
- Workflows live under **`workflows/<slug>/`** — **no numeric `NN-` prefix** (e.g. `21-stay-status-reconciler` → `workflows/stay-status-reconciler/`).
- **Do NOT** open PRs under `specs/core/use-cases/` in `1000-agents-hub-workflows` anymore. New/updated use-cases → PR in `agent-workflow-registry`.
- The **`use-case-authoring` skill still lives in `1000-agents-hub-workflows`** and still drives everything.
- **Always create new use cases off `master`** — it has the most recent planner.

**Repo Cheat Sheet:**

| Repo | Path | Purpose |
|------|------|---------|
| Engine/skills/scripts | `~/code/1000-agents-hub-workflows` | Core tooling |
| Registry | `.agent-workflow-registry/` (or `$AGENT_WORKFLOW_REGISTRY_PATH`) | Auto-cloned, gitignored |
| Corpus | `.corpus/api-exposure-inventory/` | Endpoint validation |

---

### A2. Environment Prerequisites (One-Time Setup)

| Requirement | How to Set Up | Notes |
|-------------|---------------|-------|
| Python 3.13 + `uv` | Project venv; run everything with `uv run --quiet python …` | Bare `python3` misses deps |
| AWS SSO — `pm` profile | `aws sso login --profile pm` (use `--no-browser` to get the code) | Covers CodeArtifact (uv), Bedrock, Vault-creds read |
| Corpus | `bash .cursor/skills/use-case-authoring/scripts/ensure-corpus.sh` | Never author endpoints from memory — corpus is SSOT |
| Knowledge repos + api-sdk (MCP index) | `bash .cursor/skills/use-case-authoring/scripts/ensure-knowledge-repos.sh` | Needs **pnpm** + **CodeArtifact npm** access |
| Registry env | The ensure script writes `.registry.env`; `source .registry.env` | Sets `AGENT_WORKFLOW_REGISTRY_PATH` |

**Session Start:** Run the env doctor and clear every run-blocking ✗ before any local run:
```bash
uv run --quiet python scripts/pipeline/check_env.py --uc <slug> --env staging
```

Mint a fresh Guesty token if the cache is stale (`python scripts/local/authn.py`), TTL > 60s.

---

### A3. Author the Use Case

1. Ensure corpus is up (step above). Author **from master**.
2. Invoke the **`use-case-authoring`** skill (a.k.a. `/use-case-authoring`). It runs the PM guided intake and generates: `workflow.yaml`, `use-case.md`, `uc.toml`, `decisions.md`, `configs/agentcore-identity.json`, `runs/`.
3. It outputs into the registry (`workflows/<slug>/`). Slug is kebab-case, no NN prefix.
4. Keep it **lean-first**: read/evaluate only, minimum viable DAG, then add complexity. Every workflow ends in a `WORKFLOW_OUTPUT` node.
5. Resolve every `CALL_OAS` against the corpus by METHOD + PATH (never invent endpoints).

**Structural gate:**
```bash
uv run --quiet python scripts/pipeline/validate_uc_schema.py <path-to-uc>
```

---

### A4. The 3 MANDATORY Capabilities (No Prod Without These)

> **Gil's rule:** *"No one is allowed to put his new agent live on prod if he did not add: **Evals, Links (resources declaration), Status (attention criteria)**."*

Run the 3 prompts below one by one with the skill. Target line: `Staging: staging13. Use the default GUESTY_ACCOUNT_ID.`

#### A4a. Evals

**Prompt:**
> I want to check the quality of use case {{your use case}}. I want to reinforce or create if it does not exist the specific guidelines to evaluate the workflow. You can check in staging grafana or in prod if you can see existing runs/findings/score that would be relevant to specify specific guidelines.
> `/eval-grafana-dashboard`  `/eval-authoring`

- In `workflow.yaml`: an `end_to_end` `llm_judge` eval with `judge_criteria` derived from the workflow's success conditions (or documented opt-out in `uc.toml [evals] none=true`).

#### A4b. Status (Attention Criteria)

**Prompt:**
> I want to create attention criteria for the {{your use case}} using `/use-case-authoring`

- The updated schema **requires** a top-level `attention_gate` (Gate Floor G8) with the structured format:

```yaml
attention_gate:
  criteria_prompt: |
    ## Attention criteria
    <one sentence: when a completed run needs PM attention>
    ### Criteria:
    | Criteria name | Relevant fields | Logic / Rules | Severity |
    |---|---|---|---|
    | <name> | <output fields from runOutput> | <condition> | HIGH/MODERATE/LOW |
  read_from: runOutput   # MUST equal workflow.output_key
```

#### A4c. Links (Resource Declarations)

**Prompt:** *"Use the use-case-authoring skill to backfill resource declarations on an existing use case."*

**8-Step Task:**
1. In each `WORKFLOW_OUTPUT` node's `system_prompt`, collect every entity type named in the summary (owners, reservations, guests, listings…).
2. Resolve each `url_template` via the **MCP index** (`index.lookup_by_method_path` / `lookup_by_operation_id` on the CALL_OAS that fetches it → `operation.url_template`). Normalize placeholders to `{id}`. **If `url_template` is None → omit** that entity (no frontend page). Never invent one.
3. Add to the WORKFLOW_OUTPUT node:
   ```yaml
   resource_declarations:
     - domain: properties
       resource: listing
       url_params:
         id: "$.<jsonpath in extracted_values to entity _id>"
       name_source: "$.<jsonpath to display name>"
       url_template: "/properties/{id}"
   ```
4. Validate → run locally → confirm the `"resources"` key is present in the response and each has a real `id` + filled URL → regenerate `validation.json` until `resource_links_declared` **and** `resource_links_coverage` = pass.

> **Gotcha:** The JSONPaths point into `extracted_values`. If you clear bulky state to keep the LLM echo small, you delete the arrays the links need — so keep a **slim `[{id,name}]` array** (e.g. `listingLinks`) in state and point the declaration at that.

---

### A5. Validate + Run Locally (staging13, default account)

Local executor server is async — **invoke, then poll**:
```bash
bash scripts/start-executor-local.sh                    # boots server on :8080 (builds venv first time)
bash scripts/invoke-executor-local.sh --uc <slug> --env staging
# then poll:
curl -s -X POST localhost:8080/invocations -H "Content-Type: application/json" -d '{"action":"poll"}'
```

- First call returns `{status:"running", run_id}`. Poll with `{"action":"poll"}` until `status` != running.
- The gateway requires the `x-sub-token` header — the invoke script builds it; a hand-rolled curl without it gets `400 Missing x-sub-token`.
- After the run: `uv run python -m scripts.pipeline.generate_localrun_md --log <server-log> --variant default --uc-dir <path>`.
- Confirm `resources` present, IDs match the run log, URLs filled.

---

### A6. validation.json (Quality Gate)

```bash
AWS_PROFILE=pm uv run --quiet python -m scripts.pipeline.build_validation_manifest --uc <path>
```

- **Not CI-blocking by design, but get all checks green.**
- The `use-case-authoring` skill should handle it. If stuck, paste this prompt: **"Please LMK why and which steps fail and what we should do in order to fix them."**
- Needs the api-sdk MCP index → see §A8 if it 404s.

---

### A7. PR to the Registry

- Branch off registry `master`, put the UC under `workflows/<slug>/`, commit, push, open PR on **`guestyorg/agent-workflow-registry`**.
- Title format: `SYN-XXXX | feat(<slug>): …` (link the Jira).
- **Code-owner review required** — `guestyorg/okta-cortex` and/or `team_ai_platform` (a.k.a. Cortex team) must approve to merge. Ping them.
- Registry checks: `workflow_compile_check` must PASS; if there was deterministic PYTHON_CALL logic, add `validation-cases.yaml` and run `workflow_logic_cases`.

---

### A8. Deploy + Backoffice + Status

1. **Promote the prompt** (creates the Bedrock **PROMPT ARN**). The ARN is a required field when creating the agent in the backoffice.
2. **Create/enable the agent in the backoffice**; set status correctly: **ACTIVE** or **DEV** only — **"coming soon" is not really supported and still shows in the UI.**
3. Test in prod on a QA account.

---

### A9. Known Blockers & Fixes

| Issue | Solution |
|-------|----------|
| **api-sdk build 404 (`@guestyci/rafiki … Not Found`)** | The MCP index/validation manifest needs Guesty's **private npm registry** via **CodeArtifact** (`mgmt`/`pm`), and **pnpm**. Install pnpm to a user prefix (`npm config set prefix ~/.npm-global && npm i -g pnpm`), then you still need a CodeArtifact npm login for `@guestyci`. |
| **Staging Vault migration (infra-blocked)** | Both `agentcore/staging1/vault_creds` and `agentcore/staging13/vault_creds` now resolve to `vault.staging-aux.gue5ty.com`, where `secret/agents_auth/1000_agents` returns **no data**. Needs the **platform team** to populate/repoint that secret. |
| **Executor server needs `ENVIRONMENT_NAME`** | Set (e.g. `staging13`) — matches the `credential_provider_arn` suffix `1000-agents-<env>`; missing it → `KeyError: ENVIRONMENT_NAME` at boot. |
| **`.env.staging` placeholders break `source`** | Unfilled `<...>` values contain shell redirection chars; fill from Vault or blank them. |
| **"Input too long" at WORKFLOW_OUTPUT** | The LLM echo serializes `extracted_values`; the FOR_EACH `collect_results_key` is stored there too and each entry embeds a full state copy (~O(n²)). Clear bulky arrays in the final PYTHON_CALL before the output node. |
| **Rate limiting (429) on large accounts** | Per-listing GETs get throttled; master now has CALL_OAS retry/backoff. For huge accounts the un-truncated list can exceed the output token cap (~650–700 items) — summarize the bulk list. |
| **Orchestrator vs local server** | The deterministic orchestrator's single-POST run stage sees `{status:running}` (async), so its assess may read "no-run" even when the workflow runs fine. Prove execution via poll. |
| **Cursor token limit** | You may hit it mid-build; ask Gil/Sapir for more. |

---

### A10. Content, Copy & Help Center (Product-Facing — Don't Skip)

- **Copy MUST be reviewed** — go over the **"what it does"** and the backoffice description with **Toby** (or at least **Atlas**); keep it **concise** (no essays). Use shipped UCs 1–11 as reference.
- Validate the **bullet-point description in the drawer** when the agent is selected.
- Use **Toby's copy guide** (in the shared "Evaluations/guide" Google doc) for descriptions, titles, marketing video copy.
- **Every new agent needs a Help Center (HC) article** — "an important part, like any other feature."
- Category: agents can be relevant to multiple domains (multi-select was requested; check current UI).

---

### A11. Monitoring & Rollout

- **Acknowledge you are monitoring.** Use the **monitoring guide** (Google doc), the **Grafana dashboard** (staging + prod runs/error rates), and the **Hub dashboard** (DataStudio, agent-table level).
- Watch error rates per agent; PMs own their agents' failures (take issues to your TL / `#contact-1000-agents`).

**Rollout Stages:**

| Stage | Criteria |
|-------|----------|
| **Dev** | Initial development |
| **Pilot** | Accounts < 400 listings |
| **Beta** | 400–600 listings |
| **GA** | Full rollout |

Confirm confidence before expanding to large / ENT accounts. Pilot uses a feature-flag/FT name — ask Gil for the current one to add to a test account.

---

### A12. Agent Design Pitfalls (From the Channel)

- **Channel policy rules** — e.g. inquiry-expiry / auto-decline agents must **exclude VRBO** reservations (violates VRBO policy). Check each OTA's rules before acting on their reservations.
- **Don't spam the tasks infra** — Reviews Response / Reservation Risk Spotter / Double Booking Resolver flagged for high task-creation risk. Gate task creation tightly.
- **Re-run UX** — no indication when an agent is already running, and re-click returns a misleading "failed" instead of "already running." Don't design around instant re-runs.
- **Properties/large-account timeouts** — a known `Workflow execution timeout` on property-heavy accounts; present the use case to your TL (Aram) for the recommended mitigation.
- **Test accounts that fail** — Casago / Avari accounts have had recurring failures (esp. accounting agents); test against representative accounts, not just the default.
- **Only active + listed** entities where relevant — filter out inactive/unlisted.

---

### A13. Reference Links

| Resource | Location |
|----------|----------|
| Registry repo | `github.com/guestyorg/agent-workflow-registry` |
| Engine/skills repo | `github.com/guestyorg/1000-agents-hub-workflows` |
| Gil's walkthrough | Loom `be7c1ca153aa41ebb275bec0bd8f0500` (audio broken — use the 3 prompts instead) |
| Monitoring + copy guide (Toby) | Google doc `1Awe6zZsNyOXAaPtXhbWfgvZ0yHW2JbT7ZROtE4GrseI` |
| Activation tracker | Sheet `1c4kssJx8b0-LXwoDRheIM8NwmWd7hwMa3YvZgIxvHwE` |
| Help/TLs | `#contact-1000-agents` |

---

*Last updated: July 2026*
