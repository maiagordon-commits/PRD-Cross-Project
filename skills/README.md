# Skills Catalog
> Suggested project-management automation skills for future Cursor agents working in this vault.

## Purpose
This directory documents useful skill patterns for maintaining Maia Gordon's Guesty project-management vault. These are local operating notes, not live integrations by themselves.

## Recommended skills

### Meeting-note ingestion
- Input: raw meeting notes, transcript, agenda, or summary.
- Output: synthesized meeting summary, decisions, action items, risks, dependencies, and wiki updates.
- Update: `wiki/meetings/`, relevant project pages, `Decision Log.md`, `Risk Register.md`, `Dependencies.md`, `Master Wiki Index.md`, and `log.md` as needed.

### Weekly status report
- Input: Jira status, meeting notes, Slack summaries, risk register, dependency register, and project pages.
- Output: concise weekly summary with project health, progress, risks, decisions needed, and action items.
- Update: `wiki/status/Status Reports.md` and `log.md`.

### Jira issue/status summary
- Input: Jira issue, board, epic, initiative, or export.
- Output: durable issue analysis, project status summary, risks, dependencies, and follow-up questions.
- Rule: Jira remains the source of truth for live task status.

### Slack channel summary
- Input: Slack channel or thread export/summary.
- Output: source-backed summary of decisions, blockers, stakeholder updates, and action items.
- Rule: Preserve links and avoid copying sensitive content unless approved.

### Risk and blocker review
- Input: project pages, Jira blockers, Slack escalations, meeting notes, and dependency table.
- Output: updated `Risk Register.md` with owners, next steps, impact, and source links.

### Decision-log maintenance
- Input: meeting notes, Slack threads, Confluence docs, Jira comments, or stakeholder confirmations.
- Output: updated `Decision Log.md` and affected project pages.
- Rule: Do not log a decision unless the source clearly supports it.

### Stakeholder update drafting
- Input: project pages, status reports, risk register, and audience.
- Output: short stakeholder-specific update with progress, risks, asks, and next steps.

### Project health check
- Input: project page, Jira status, risks, dependencies, recent meetings, and stakeholder updates.
- Output: health rating, key concerns, stale info, decisions needed, and recommended next actions.

### Launch / milestone checklist
- Input: project scope, milestone target, dependencies, owners, validation requirements, and rollout plan.
- Output: checklist of readiness, risks, owners, communications, and launch follow-up.

### Confluence-to-wiki ingestion
- Input: Confluence page or exported content.
- Output: raw source record plus synthesized wiki updates with source links.
- Rule: Keep Confluence as source evidence; synthesize durable knowledge into `wiki/`.

