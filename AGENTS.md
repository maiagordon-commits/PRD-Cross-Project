# Guesty Project-Management Vault Operating Manual

## What this vault is
This repository is a local AI-maintained Markdown knowledge vault for Maia Gordon's project-management work at Guesty. It preserves raw source material in `raw/` and turns durable execution knowledge into concise, cross-linked pages in `wiki/`.

## Owner
- Owner: Maia Gordon
- Role: R&D and Product Project Manager
- Team/org: Product
- Reporting line: CTO
- Primary scope: Delivery of cross-team initiatives, enterprise escalations, issue analysis, requests, and internal Guesty technical programs on the roadmap.

## What the vault is for
- Execution coordination across teams and workstreams.
- Project, program, milestone, rollout, and launch context.
- Stakeholder, reporting, meeting, risk, decision, and dependency memory.
- Practical summaries that help Maia and future agents prepare updates, analyze issues, and maintain continuity.

## Folder structure
- `raw/`: Source material kept close to the original.
- `raw/meetings/`: Meeting notes, transcripts, copied agenda notes, and follow-ups.
- `raw/slack/`: Slack thread exports, copied summaries, and channel context.
- `raw/jira/`: Jira issue links, exports, filters, board notes, and status snapshots.
- `raw/confluence/`: Confluence page links, exports, and summaries.
- `raw/docs/`: Planning docs, spreadsheets, dashboards, and external document context.
- `raw/misc/`: Other unprocessed notes or evidence.
- `wiki/`: Synthesized durable project-management knowledge.
- `wiki/projects/`: Project and program pages.
- `wiki/workstreams/`: Domain and workstream summaries.
- `wiki/stakeholders/`: Stakeholder maps and reporting context.
- `wiki/meetings/`: Recurring meetings and meeting summaries.
- `wiki/decisions/`: Decision records and decision log.
- `wiki/risks/`: Risks, blockers, mitigations, and owners.
- `wiki/dependencies/`: Cross-team dependencies and external constraints.
- `wiki/status/`: Weekly/monthly status reports and project health summaries.
- `wiki/processes/`: Rituals, operating practices, and repeatable workflows.
- `wiki/templates/`: Reusable page templates.
- `skills/`: Local notes describing useful automation skills for future agents.

## Page standards
Every wiki page should begin with frontmatter:

```markdown
---
title: Page Title
area: Project Management
workstream:
type: overview | project | workstream | stakeholder | meeting | decision | risk | dependency | status | process | template
status: active | planned | paused | completed | archived
owner:
last_updated: YYYY-MM-DD
source_count: 0
tags: []
---
```

Use this structure where relevant:
- `# Page Title`
- One-line blockquote explaining why the page matters.
- `## Summary`
- `## Key Facts`
- `## Current Status`
- `## Open Questions / Gaps`
- `## Related Pages`
- `## Source Log`

## Ingestion rules
- Put unprocessed source material in `raw/`.
- Keep raw files close to the original wording.
- Preserve direct links to Slack, Jira, Confluence, docs, dashboards, and meeting recordings when available.
- Use `wiki/` only for synthesized durable knowledge.
- Do not dump messy raw notes into `wiki/`.
- When privacy is unclear, summarize and link rather than copying sensitive text.
- Maia's current privacy preference is ad hoc: decide per source, and ask when unsure.

## Query rules
- Treat Jira or the relevant tracker as the source of truth for live task status.
- Treat this vault as durable context, not a replacement for operational systems.
- Never invent facts, dates, owners, priorities, or decisions.
- If a user asks about current status and the vault lacks fresh evidence, say what is known and what must be checked.
- Prefer concise, practical answers with links to relevant wiki pages and source references.

## Logging rules
- Update `log.md` after every meaningful vault change.
- Use static dates in `YYYY-MM-DD` format.
- Use one of these types when possible: `setup`, `ingest`, `update`, `query`, `meeting`, `status`, `lint`.
- Log what changed and which pages/sources were touched.

## Index maintenance rules
- Update `Master Wiki Index.md` when creating, renaming, or deleting wiki pages.
- Keep the index organized by projects, workstreams, stakeholders, meetings, decisions, risks, dependencies, status, processes, and templates.
- Link pages using wiki-style links when useful and Markdown links when paths are clearer.

## What not to do
- Do not store secrets, credentials, tokens, or private customer data.
- Do not copy sensitive raw content unless Maia explicitly approves.
- Do not present stale Jira or Slack information as live truth.
- Do not create artificial certainty where the vault has gaps.
- Do not over-document trivial updates.
- Do not change raw source wording except for light formatting or redaction.

## Current known Guesty context
- Active/known programs: Geo Expansion, RooM Program, AI Program, Alloggio Re-onboarding, Hometime End of Month, Casago End of Month, Avari End of Month, and Translations Project.
- Documentation style preference: Standard.
- Task tracking preference: Mainly summaries, action items, and issue analysis in this vault; detailed task status should remain in Jira or the relevant system.

## Useful future skills
- Meeting-note ingestion.
- Weekly status report generation.
- Jira issue/status summary.
- Slack channel summary.
- Risk and blocker review.
- Decision-log maintenance.
- Stakeholder update drafting.
- Project health check.
- Launch/milestone checklist.
- Confluence-to-wiki ingestion.

