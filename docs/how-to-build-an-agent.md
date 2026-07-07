# How to Build an Agent — Step-by-Step Guide

A practical guide for PMs and domain owners creating agents in the **Agent Hub Workflows** repo using Cursor.

---

## Overview

An agent is a **defined workflow with LLM decision nodes**. It is deterministic: it only does what you configure it to do. It reads data, makes decisions based on that data, and takes allowed actions (for example, creating a task or posting a comment).

Agents live in the **Agent Hub Workflows** repo under `steps/use_cases/`. You do not write workflow code by hand — Cursor and the **PM Use Case** skill guide you through design, generation, and validation.

### Your responsibilities

You wear two hats:

1. **Build new agents** — target pace of ~15–20 agents per month (~1–2 per PM per month).
2. **Own existing agents** in your domain — monitor, fix, and improve them (V1 → V2 → V3).

The owning PM and team are responsible for agent quality and maintenance. Cortex builds the platform; your team owns the agent as a product feature.

---

## Before You Start: Know the Current Limitations

Validate your use case against these constraints **before** you invest time building.

| Capability | Status today | Workaround / notes |
|---|---|---|
| **Triggers** | Scheduled or on-demand only | Use scheduled runs (e.g., every 4 hours) instead of event triggers (e.g., “on new inquiry”). Event triggers planned early Q3. |
| **On-demand** | User must open Agent Hub and click **Run now** | Fine for shift-handoff style use cases; awkward for most automation. |
| **API access** | Open API (external) endpoints only | If data is missing, ask your dev team to expose an endpoint. Internal-only APIs for agents planned early Q3. |
| **Target a single record** | Not supported (e.g., one reservation by ID) | Run on a filtered set (e.g., all reservations checking in today). |
| **Human-in-the-loop** | Not supported | Agents run fully autonomously or create tasks/comments. Approval flows planned early Q3. |
| **File upload / file output** | Not supported | Planned for Q3. |
| **Links in output** | Rolling out | Links to reservations and tasks coming for June release. Smart-view deep links are a separate use case. |
| **Notifications** | No API yet | Planned ~end of July. |
| **Time zones** | Eastern for all accounts | Account time zone support coming soon. |
| **Run status / “handled” marking** | Limited | Activity feed shows runs; no “mark as done” yet. Filter by status and domain. |

If your ideal use case is blocked, either **compromise** (change trigger, scope, or output) or **swap the use case** for June. Flag repeated blockers to Cortex — they may reprioritize platform work.

---

## Phase 1 — Prepare Your Use Case

### 1. Review the use case sheet

The use case sheet is the **source of truth**. For June delivery:

- Confirm your use case is marked for the target release.
- Re-read it with the limitations above in mind.

### 2. Decide on compromises

Example from the session: an “inquiry chaser” ideally triggers on every new inquiry. Today you might run every 4 hours over reservations in a given status instead.

Ask yourself:

- Can this run on a **schedule** instead of an event?
- Can it run on a **batch** (e.g., all check-ins today) instead of one record?
- Is the **output** a comment, task, or activity summary — and is that enough for v1?

### 3. Check API coverage

Agents can only call endpoints that exist in the **Open API**.

- Browse what is available (work with your dev team / improved OpenAPI spec).
- If an endpoint is missing, open a request with your team — exposure is often fast (same-day in some cases).
- You do **not** need to manually update Cortex docs when your team adds an endpoint; still loop in Cortex if integration issues appear.

### 4. Gather domain context (only when needed)

Simple, well-defined workflows (e.g., security deposit checks) may need no extra context.

Complex judgment calls (e.g., “risky reservation”) benefit from written criteria, examples, and edge cases. You can attach:

- Supporting documents
- Reference repos
- Files dragged into Cursor

**Do not add context just because you can** — add it when the agent needs domain judgment.

### 5. Align with your TL

Your tech lead will help with deployment, deeper testing, and API exposure. Sync early if you need new endpoints or unusual scope.

---

## Phase 2 — Create the Agent in Cursor

### 1. Open the repo

Clone/open **Agent Hub Workflows** in Cursor.

Existing agents live under `steps/use_cases/`. Your new agent will be added there as a new use case folder with workflow YAML and metadata.

### 2. Start the PM Use Case skill

In Cursor chat:

```
/skill PM use case
```

**Recommendations:**

- Do **not** use Auto mode for this flow — use a capable model with skills enabled.
- Stay in the same chat through design and PR creation when possible.

### 3. Provide a brief description

Paste or write a concise description of what the agent should do.

**Example (shift handoff):**

> Read the reservation conversation, notes, and comments and produce a concise handoff summary so whoever picks up a shift or escalation is caught up instantly.

---

## Phase 3 — Answer the Skill’s Questions

The skill walks you through product decisions. Expect questions like these:

### Trigger

| Option | Meaning |
|---|---|
| **Scheduled** | Runs automatically (e.g., every 4 hours, daily, monthly). You define frequency and start time. |
| **On-demand** | User opens Agent Hub and clicks **Run now**. |
| **Both** | Scheduled runs plus manual run. |

Choose based on user workflow, not what is easiest to demo.

### Scope — what records does it run on?

Define the starting set. Examples:

- All reservations **checking in today** (not checking out).
- All reservations in a given status.

You cannot today say “run on reservation ID 12345” or “run when user picks a guest name.”

### What data should it read?

Select data sources the agent needs. Common options:

- Conversation / messages
- Reservation details
- Reservation notes
- Reservation comments
- Related tasks
- Booking channel, guest info, checkout date, special requests, etc.

The skill checks Open API availability. If something is not exposed, it will flag it — drop it or ask your team to expose the endpoint.

**Tip:** More data is not always better. Scanning everything may add noise without improving the handoff.

### Filters and prioritization

Optional. Examples:

- Only unresolved messages
- Only notes from the last N hours

If unsure, keep v1 simple.

### What should it output?

Typical outputs today:

| Output | Notes |
|---|---|
| **Activity summary** | Compact 2-line summary per run in Agent Activity |
| **Reservation comment** | Posted on the reservation |
| **Task** | Created with instructions / next steps |
| **Links** | To reservation or task (rolling out) |

Not available yet: notifications, file artifacts, human approval gates.

### Human approval

Today: **fully automated**. The skill may ask about approval — answer **no** for current platform behavior.

### Additional artifacts

Beyond the main summary, do you want per-reservation comments, tasks, etc.? Decide explicitly to avoid noisy outputs (e.g., a comment on every reservation in a large batch).

### Enrichment data

The skill may suggest extra fields for the handoff (checkout date, booking channel, security deposit status, etc.). Accept only what adds value.

### Supporting documents

Add files or references if domain context is required.

---

## Phase 4 — Review the Workflow Summary

Before any code is generated, the skill presents a **business summary** of the flow:

- Trigger and schedule
- Data sources
- Decision logic
- Outputs and side effects

**You must review this carefully.**

- Does the scope match what you intended?
- Are the outputs correct (comment vs. task vs. summary only)?
- Did it assume data that is not in the Open API?

Accept only when accurate. Change trigger, scope, or outputs in chat before proceeding.

---

## Phase 5 — Build and Auto-Validate

When you confirm, the skill:

1. Generates the **workflow YAML** and **use case** files.
2. Tests calls against the **Open API**.
3. Fixes parameter and schema issues where possible.

This step can take time. The skill may iterate — for example, correcting API field names or dropping unavailable fields.

---

## Phase 6 — Review Generated Artifacts

Each use case folder includes:

| Artifact | Who reviews | What to check |
|---|---|---|
| **Use case definition** | PM (required) | Intent, steps, and decisions in plain language |
| **Workflow YAML** | PM + TL | Step descriptions; overall flow |
| **Decision tree** | PM (light) | Branching matches product intent |

### PM review checklist

- [ ] Trigger and scope are correct
- [ ] Data sources exist in Open API
- [ ] Outputs match what you specified (no surprise comments on every record)
- [ ] No hallucinated URLs or unsupported actions
- [ ] Risky autonomous actions are avoided for v1 (e.g., do not allow “delete reservation” if the API supports it)

---

## Phase 7 — Test Locally

> Available once local run is enabled in the repo (expected shortly after the intro session).

### Setup

1. Run the local agent command in Cursor.
2. Provide a **test account ID** (staging strongly preferred).
3. Provide **Open API credentials** for that account.

### What to verify

**Technical**

- APIs return success responses.
- Returned data matches reality (e.g., if you expect “co-host staying,” the API actually returns that).

**Business**

- Happy path works end to end.
- Edge paths behave as expected (failed payments, different booking channels, empty notes, etc.).
- Agent does nothing when it should do nothing.

**Cross-channel**

- Schemas differ by channel (e.g., Booking.com vs. Airbnb reviews). Test each relevant channel.

### Testing gaps

Staging may lack real channel connections or specific account states. If you are blocked:

- Document exactly what account/data you need.
- Escalate early — this is a known platform-wide testing challenge, not only an agents issue.

Domain experts and TLs should help design test matrices.

---

## Phase 8 — Ship via Pull Request

### 1. Create a Jira ticket

Every agent should have a ticket for traceability.

### 2. Create a branch

Naming convention (adapt to your team prefix):

```
<TICKET-ID>-<short-use-case-name>
```

Example: `TRTX-1234-usecase-handover`

Some repos require a specific prefix (e.g., `CRTX-`) — follow repo conventions.

### 3. Open a PR

In Cursor, ask it to create a PR from your branch. Include:

- Clear PR title (ticket + use case name)
- Short description of what the agent does
- Target environment: **staging** or **production**

### 4. Review and merge

- Post the PR link in the **#100-agents** Slack channel.
- Cortex reviews for now; later, your TL may review.
- This repo may have **fewer automated CI checks** than other repos — manual testing matters more.
- PRs do not auto-merge; a reviewer must approve.

### 5. Enable in Agent Hub

After merge/deploy:

- Agent appears as a **tile** in the Agents marketplace.
- Enable for pilot accounts.
- Category and marketplace description should be automated over time; confirm they look correct.

---

## Phase 9 — Monitor and Iterate

### Agent Activity feed

Each run shows:

- Status: done, needs attention, requiring action, failed
- Compact output summary
- Detail view for full run output

Filter by **status** and **domain** (e.g., Operations). Per-agent filters may be added.

### Ownership expectations

- Watch pilot accounts manually at first.
- Collect user feedback.
- Fix bad outputs (e.g., hallucinated links — known issue with fixes in flight).
- Plan V2: better triggers, richer outputs, evaluations.

### Observability (improving)

Cortex is building:

- PM-facing trace dashboards
- Golden-set evaluations
- LLM-as-judge run quality checks

Until then, treat **manual review** as part of the job.

### Agent actions in logs

When an agent changes a reservation or creates a task, logs should indicate it was done **via Guesty** / the agent name.

---

## Quick Reference — End-to-End Checklist

```
[ ] Use case validated against platform limitations
[ ] Use case sheet updated (source of truth)
[ ] Open API endpoints confirmed (or exposure requested)
[ ] Domain context prepared (if needed)
[ ] /skill PM use case started in Agent Hub Workflows repo
[ ] Trigger, scope, data, and outputs defined
[ ] Workflow summary reviewed and accepted
[ ] Artifacts generated and reviewed (use case + workflow)
[ ] Local test on staging account — happy path + edge cases
[ ] Jira ticket created
[ ] Branch + PR opened and posted to #100-agents
[ ] PR approved and merged
[ ] Agent enabled for pilot
[ ] Activity monitored; feedback captured for V2
```

---

## FAQ

**Can I inject extra instructions beyond the skill’s questions?**  
Yes. Add context in chat or attach docs — especially for judgment-heavy agents.

**Do I need to connect my domain’s main app repo?**  
No. The agent repo works against Open API. It does not need your service repo connected.

**What if my use case needs Booking API / Channel API?**  
Expose what you need through Open API with your team. Cortex is not planning to add non-Open API surfaces for agents in the near term.

**What about rate limits?**  
Cortex handles agent rate limiting separately from standard Open API client limits.

**What if Open API changes break my agent?**  
API deprecation has a 4–6 month notice process. Coordinate with your team on schema changes. Dedicated agent error observability is being built.

**Should I build high-risk agents first?**  
No. Start with read-heavy or low-risk outputs (summaries, tasks). Avoid autonomous destructive actions in early pilots.

---

## Example Walkthrough — Shift Handoff Agent

| Step | Decision |
|---|---|
| Description | Summarize conversation, notes, and comments for shift handoff |
| Trigger | On-demand (user runs at shift change) |
| Scope | All reservations checking in today |
| Read | Conversation, reservation details, notes, comments, related tasks |
| Filter | None for v1 |
| Output | Reservation comment with handoff summary + activity feed summary |
| Approval | None (fully automated) |
| Enrichment | Checkout date, booking channel, guest details |
| Testing | Staging account with multi-note reservations; empty conversation edge case |
| Ship | PR → review → enable for pilot ops accounts |

---

*Derived from the Agent Hub onboarding session. Platform capabilities evolve — confirm current limitations with Cortex before building.*
