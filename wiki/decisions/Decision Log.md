---
title: Decision Log
area: Project Management
workstream:
type: decision
status: active
owner: Maia Gordon
last_updated: 2026-06-01
source_count: 2
tags: [decisions]
---

# Decision Log
> This page records durable decisions, rationale, owners, and source links.

## Summary
Use this log to capture decisions that affect scope, delivery, timelines, ownership, rollout, escalation handling, or stakeholder alignment. Decisions should be clear, source-backed, and linked to affected projects.

## Key Facts
- Capture the decision, date, owner/approver, rationale, impact, and source.
- Do not infer decisions from vague discussion.
- If a source only suggests a possible direction, record it as an open question instead.

## Current Status
- Decisions from the PMS Data Mirroring workshops have been logged.

## Open Questions / Gaps
- Which existing decisions from Jira, Slack, Confluence, or meetings should be backfilled?

## Decision Table
| Date | Decision | Project / Workstream | Owner / Approver | Source | Impact |
|------|----------|----------------------|------------------|--------|--------|
| 2026-05-20 | Financial reconciliation for migrations will mirror the old PMS, not channel data, when matching customer expectations from the legacy system. | Channels and Financials / PMS Data Mirroring | Workshop participants | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H) | Implementation can reconcile against legacy financial reporting while Guesty imports channel data. |
| 2026-05-20 | Channel data remains the source of truth for Guesty imports. | Channels and Financials / PMS Data Mirroring | Workshop participants | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H) | Guesty should not invent imported channel data from old PMS values. |
| 2026-05-20 | Host payout discrepancies between legacy systems and channels are the customer's responsibility to resolve. | Channels and Financials / PMS Data Mirroring | Workshop participants | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H) | Implementation should provide discrepancy reports instead of silently reconciling impossible mismatches. |
| 2026-05-20 | Rent adjustments will mirror the source system when fees are bundled, with realization dates aligned to customer revenue recognition. | Channels and Financials / PMS Data Mirroring | Workshop participants | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H) | Reconciliation must handle amount and accounting-date alignment. |
| 2026-05-28 | The financial mapping tool should include intake/mapping and output/settings components. | Channels and Financials / PMS Data Mirroring | Workshop participants | [Workshop 2](https://fellow.link/QWH0FDG5XDC4) | Product direction favors creating settings or setting snapshots rather than recurring manual adjustments. |
| 2026-05-28 | Channel fees should remain visible on folios while adjusted fees are applied as settings in the background. | Channels and Financials / PMS Data Mirroring | Workshop participants | [Workshop 2](https://fellow.link/QWH0FDG5XDC4) | Preserves channel source-of-truth visibility while making migrated financial output usable. |

## Related Pages
- [[../projects/Projects]]
- [[../risks/Risk Register]]
- [[../dependencies/Dependencies]]
- [[../templates/Decision Template]]

## Source Log
| Date | Source | What was added |
|------|--------|----------------|
| 2026-06-01 | PMS Data Mirroring workshop summaries | Added decisions from the two workshops. |

