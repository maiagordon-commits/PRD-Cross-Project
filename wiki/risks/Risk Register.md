---
title: Risk Register
area: Project Management
workstream:
type: risk
status: active
owner: Maia Gordon
last_updated: 2026-06-01
source_count: 2
tags: [risks, blockers, escalations]
---

# Risk Register
> This page tracks risks, blockers, owners, mitigations, and next steps across Maia's projects.

## Summary
Use this register for delivery risks, cross-team blockers, stakeholder escalations, launch concerns, and unresolved dependencies. Each risk should include an owner, current status, impact, next step, and source when available.

## Key Facts
- Risks should be practical and actionable.
- Enterprise escalations and issue-analysis findings can be summarized here when they affect delivery.
- Do not treat this page as a replacement for live Jira issue status.

## Current Status
- PMS Data Mirroring workshop risks have been logged.

## Open Questions / Gaps
- Which active projects have known blockers?
- Which risks need leadership visibility?
- Which risks depend on customer, business, engineering, data, or operations teams?

## Risk Table
| ID | Risk / Blocker | Project / Workstream | Impact | Owner | Status | Next Step | Source |
|----|----------------|----------------------|--------|-------|--------|-----------|--------|
| R-001 | VRBO provides lumped tax data and low-quality fee/tax reservation details. | PMS Data Mirroring / Distribution | Manual tax reconstruction remains expensive and can create compliance risk. | Distribution / Javier | Open | Reopen VRBO discussion and push for granular tax breakdown. | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H), [Workshop 2](https://fellow.link/QWH0FDG5XDC4) |
| R-002 | Imported fees can reverse-map into incorrect or missing Guesty fee settings. | PMS Data Mirroring / Financials | Accounting mappings, owner statements, and imported folios can be wrong. | Financials Product / Rinat | Open | Document reverse-mapping and default-fee behavior gaps. | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H), [Workshop 2](https://fellow.link/QWH0FDG5XDC4) |
| R-003 | Legacy PMS data can be unreliable or internally derived. | PMS Data Mirroring / Implementation | Guesty cannot safely reconcile some host payout or fee deltas without customer input. | Implementation / Alex | Open | Provide discrepancy reports and get customer guidance when source systems disagree. | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H) |
| R-004 | Regional tax rules differ materially across APAC, EMEA, and US. | PMS Data Mirroring / Financials | A global import rule may create legal or compliance exposure. | Financials Product / Legal | Open | Validate regional tax handling before productizing import rules. | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H), [Workshop 2](https://fellow.link/QWH0FDG5XDC4) |
| R-005 | BEAST migration tools may not override locked periods. | Avari / Hometime End of Month | Owner-statement deadlines and migration completion can be missed. | Financials Product / Tier 3 | Open | Run Tier 3/API fallback and investigate BEAST behavior. | [Workshop 2](https://fellow.link/QWH0FDG5XDC4) |
| R-006 | Rates-and-availability behavior may affect customers whose fees were not bundled into accommodation fare. | Distribution / Rates and Availability | Customer communication may create compensation or liability exposure. | Distribution / Legal / Product | Open | Create impacted-customer report and review legal exposure. | [Workshop 2](https://fellow.link/QWH0FDG5XDC4) |

## Related Pages
- [[../projects/Projects]]
- [[../dependencies/Dependencies]]
- [[../status/Status Reports]]
- [[../templates/Risk Template]]

## Source Log
| Date | Source | What was added |
|------|--------|----------------|
| 2026-06-01 | PMS Data Mirroring workshop summaries | Added risks from the two workshops. |

