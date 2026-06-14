# OTA Financial Data Mapping Playbook

**Product department reference — reverse engineering & migration**  
**Last updated:** June 14, 2026  
**Sources:** Internal Workshop #1 (May 20, 2026) · Internal Workshop #2 (May 28, 2026) · Slack `#reverse-mapping-ga` · Confluence · Jira

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Workshop Participants & Context](#2-workshop-participants--context)
3. [Decision Log](#3-decision-log)
4. [Source of Truth Framework](#4-source-of-truth-framework)
5. [Topic: Reverse Mapping & Migration Scope](#5-topic-reverse-mapping--migration-scope)
6. [Topic: Fee Mapping & Configuration](#6-topic-fee-mapping--configuration)
7. [Topic: Taxes & Legal Compliance](#7-topic-taxes--legal-compliance)
8. [Topic: Reservation Settings & Manual Adjustments](#8-topic-reservation-settings--manual-adjustments)
9. [Topic: Import Mapping Rules (BDC, VRBO, Airbnb)](#9-topic-import-mapping-rules-bdc-vrbo-airbnb)
10. [Topic: Data Quality & Known Bugs](#10-topic-data-quality--known-bugs)
11. [Topic: Beast Tool & Operational Workflows](#11-topic-beast-tool--operational-workflows)
12. [Topic: AI Agent & Settings Snapshots (Roadmap)](#12-topic-ai-agent--settings-snapshots-roadmap)
13. [Topic: Rates & Availability Toggle Removal](#13-topic-rates--availability-toggle-removal)
14. [Topic: Customer Support & Enterprise vs SMB](#14-topic-customer-support--enterprise-vs-smb)
15. [Topic: Regional Complexity (Australia, GST)](#15-topic-regional-complexity-australia-gst)
16. [Implementation Guidance by Phase](#16-implementation-guidance-by-phase)
17. [Action Items & Open Questions](#17-action-items--open-questions)
18. [Appendix: Related Links & Source Files](#18-appendix-related-links--source-files)

---

## 1. Executive Summary

This playbook consolidates two internal workshops on OTA financial data reverse engineering and migration. It is intended for the Product department to align on **what we decided**, **why**, and **how to implement** financial data mapping during PMS-to-Guesty transitions.

### Core problem

When migrating accounts from legacy PMS systems (Guesty Lite, Avari, etc.) to Guesty Pro, financial data from OTAs (Booking.com, Airbnb, VRBO) must be mapped correctly. Channels send reservation-level financial payloads; legacy PMS data may differ. The team must decide **which source wins** and **who owns reconciliation** when they conflict.

### Strategic direction (Workshop #2)

| Phase | Approach | Status |
|-------|----------|--------|
| **Phase 1 (MVP — July 10 release)** | AI agent converts CSV exports → automated mapping | In development |
| **Phase 2** | Settings-based snapshots on reservations (replace manual adjustments) | Planned — estimated to reduce Avari maintenance from 5–6 hrs/month to ~30 min |
| **Long term** | No universal one-size-fits-all import — regional/account variation requires flexible tooling | Accepted constraint |

### Key principles (both workshops)

- **Migrated accounts mirror previous PMS data**, not strictly channel data — unless channel is legally required (taxes).
- **Customer is liable** for resolving discrepancies when channel is source of truth but conflicts with legacy data.
- **Client owns financial reconciliation accuracy** — we provide imbalance reports, not universal migration fixes.
- **Manual reservation overrides are not reverted** by channel updates (validated by Alex's testing).
- **Tax adjustments are prohibited** — prioritize channel tax data for legal remittance.

---

## 2. Workshop Participants & Context

### Workshop #1 — May 20, 2026

| Participant | Role / Contribution |
|-------------|---------------------|
| Maia Gordon | Product lead, workshop facilitator |
| Alex Borack | Engineering — manual override testing, Beast tool |
| Ella Waldman | Product / migration strategy |
| Javier Ibarz | Engineering |
| Rinat Elimelech | Product |
| Vadym Padalko | Engineering |
| Eyal Razi | Product / operations |

### Workshop #2 — May 28, 2026

Same core group; additional context from Rotem Meir (enterprise accounts). Focus shifted to **July 10 release**, **AI agent MVP**, **settings snapshots**, and **Rates & Availability toggle removal**.

### Background

- Reverse mapping GA rollout ongoing; ~2,000 BDC reservations need Deduct 2.0 migration (T3 escalation path).
- Beast tool used for bulk financial corrections; known issues with locked accounting periods.
- Avari accounts require 5–6 hours/month of manual maintenance — settings snapshots target ~30 min.

---

## 3. Decision Log

### Aligned — Workshop #1 (May 20)

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Migrated accounts should mirror **previous PMS data**, not strictly channel data | Preserves customer expectations from legacy system |
| D2 | Customer is **liable** for resolving discrepancies when channel is source of truth but conflicts with legacy | Avoids Guesty owning reconciliation liability |
| D3 | **Account-level fee workaround:** add $1/day per fee type at account level to prevent mapping failures | Prevents import failures when fee types missing |
| D4 | **Tax adjustments prohibited** — prioritize channel tax data | Legal remittance requirements |
| D5 | **Client owns** financial reconciliation accuracy | Support model boundary |
| D6 | Manual reservation overrides **not reverted** by channel updates | Alex validated; protects customer edits |
| D7 | Provide clients **imbalance reports**, not universal migration fixes | Scalable support model |
| D8 | Enterprise white-glove support vs SMB self-service | Tiered support approach |

### Needs Further Discussion — Workshop #1

| # | Topic | Notes |
|---|-------|-------|
| O1 | Default fee configuration / system-level fee dictionary for new accounts | No final strategy |
| O2 | Final strategy for financial import discrepancy resolution | Partially addressed in WS2 |

### Aligned — Workshop #2 (May 28)

| # | Decision | Rationale |
|---|----------|-----------|
| D9 | **July 10 release** confirmed for reverse mapping / AI agent MVP | Product milestone |
| D10 | Transition to **reservation settings as source of truth** (replacing manual adjustments) | Phase 2 architecture |
| D11 | Remove **Rates & Availability feature toggle** — legal review required first (Shan), impact report needed | Simplifies product; legal gate |
| D12 | No universal one-size-fits-all import solution | Regional variation (Australia GST, etc.) |

---

## 4. Source of Truth Framework

### Hierarchy (evolving)

```
┌─────────────────────────────────────────────────────────────┐
│  LEGACY MIGRATION (current)                                  │
│  Source of truth: Previous PMS data                          │
│  Exception: Taxes → Channel data (legal)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2 (planned)                                           │
│  Source of truth: Reservation settings (snapshots)           │
│  Replaces: Manual adjustments                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ONGOING CHANNEL UPDATES                                     │
│  Manual overrides: NOT reverted by channel                   │
│  Tax data: Always from channel                               │
└─────────────────────────────────────────────────────────────┘
```

### When sources conflict

| Scenario | Source of truth | Owner |
|----------|-----------------|-------|
| Fee amounts (migration) | Previous PMS | Customer resolves via imbalance report |
| Tax amounts | Channel (OTA) | Guesty must not adjust; customer remits per channel |
| Manual reservation edit | Reservation (customer override) | Protected from channel revert |
| Missing fee type at account | Account-level $1/day workaround | Ops/Product configure |
| BDC VAT in accommodation fare | Import mapping rules | See [Topic: Import Mapping Rules](#9-topic-import-mapping-rules-bdc-vrbo-airbnb) |

---

## 5. Topic: Reverse Mapping & Migration Scope

### Background

Reverse mapping translates OTA reservation financial payloads into Guesty Pro structures during and after migration. Scope includes Guesty Lite → Pro, Avari → Pro, and in-place BDC Deduct 2.0 migrations.

### Decisions

- **~2,000 BDC reservations** require Deduct 2.0 migration — T3 escalation path for bulk handling.
- Migrated data reflects **legacy PMS**, not a fresh channel pull — reduces surprise for customers.
- **Imbalance reports** delivered to clients; no promise of universal auto-fix.

### Implementation guidance

1. Run reverse mapping per account with documented source-of-truth rules (Section 4).
2. Generate imbalance report post-migration; client validates.
3. For BDC Deduct 2.0 backlog, coordinate with T3 for batch processing.
4. Track migration status in Jira/ops dashboards.

---

## 6. Topic: Fee Mapping & Configuration

### Background

OTAs send fees in varied structures (per-night, per-stay, bundled, zero-dollar placeholders). Legacy PMS may use different fee dictionaries. Missing fee types cause import failures.

### Decisions

- **Account-level workaround:** Add $1/day per fee type at account level to prevent mapping failures when fee type absent.
- Default fee configuration / system-level fee dictionary — **still open** (Workshop #1 O1).

### Known patterns

| Pattern | Handling |
|---------|----------|
| Zero-dollar fees (VRBO) | Data quality issue; may need manual correction or Beast |
| Bundled fees | Map to Guesty fee structure per channel rules |
| Per-night vs per-stay | Respect channel payload; document in mapping rules |
| Missing fee type | $1/day account-level placeholder |

### Implementation guidance

1. Audit account fee dictionary before migration.
2. Apply $1/day workaround for any fee types referenced in reservations but missing at account level.
3. Document fee mapping in account-specific runbook.
4. Revisit system-level fee dictionary in follow-up workshop (O1).

---

## 7. Topic: Taxes & Legal Compliance

### Background

Tax remittance is legally sensitive. Guesty must not alter channel tax data. Australia GST and regional rules add complexity (Hometime example in Workshop #2).

### Decisions

- **Tax adjustments prohibited** — always prioritize channel tax data.
- Customer responsible for remittance accuracy; Guesty provides data as received from channel.

### Implementation guidance

1. Never apply manual tax adjustments during import or Beast runs.
2. Flag tax discrepancies in imbalance report for customer review.
3. For Australia GST / tax eligibility edge cases, escalate to regional product/legal (see Section 15).
4. BDC: VAT may appear in accommodation fare — use import mapping rules (Section 9).

---

## 8. Topic: Reservation Settings & Manual Adjustments

### Background

Historically, manual adjustments were used to correct financial data on reservations. Workshop #2 aligned on moving to **reservation settings as source of truth** with snapshots.

### Decisions

- Manual reservation overrides **not reverted** by channel updates (Alex tested).
- Phase 2: **Settings-based snapshots** replace manual adjustments — target ~30 min/month Avari maintenance vs 5–6 hrs today.

### Implementation guidance

1. **Now:** Preserve manual overrides; do not overwrite on channel sync.
2. **Phase 2:** Implement settings snapshots on reservation create/update; store financial config at reservation level.
3. Deprecate manual adjustment workflows once snapshots are GA.
4. Communicate change to CS and enterprise accounts (white-glove).

---

## 9. Topic: Import Mapping Rules (BDC, VRBO, Airbnb)

### Booking.com (BDC)

- **VAT in accommodation fare:** Map per BDC payload structure; VAT may be embedded in accommodation line.
- **Deduct 2.0:** ~2,000 reservations pending migration; use T3 escalation for bulk.
- Import mapping rules documented in engineering specs — Product validates against workshop decisions.

### VRBO

- **Zero-dollar fees:** Known data quality issue; often requires post-import correction.
- **Lump-sum taxes:** May not break down by line item; map to Guesty tax structure with customer validation.

### Airbnb

- Referenced in broader reverse mapping GA; follow channel payload as secondary source except where PMS migration rules override (fees) or taxes (channel always wins).

### Implementation guidance

1. Maintain channel-specific mapping rule docs (Confluence/Jira).
2. Test import with sample payloads per channel before account migration.
3. Log unmapped fields in imbalance report.

---

## 10. Topic: Data Quality & Known Bugs

### Beast tool — locked accounting periods

- Beast **fails** when accounting period is locked.
- **Duplicates zero-dollar fees** bug — documented; avoid Beast on affected reservations until fix.

### VRBO

- Zero-dollar fees and lump-sum taxes (Section 9).

### General

- No single import path fits all regions or account configurations.

### Implementation guidance

1. Check accounting period lock before Beast runs.
2. QA zero-dollar fee duplication after Beast; rollback if detected.
3. Track bugs in Jira with link to this playbook.

---

## 11. Topic: Beast Tool & Operational Workflows

### Background

Beast is the bulk financial correction tool used by ops/engineering for migration fixes and data cleanup.

### Constraints

- Cannot run on **locked accounting periods**.
- Known bug: **duplicates zero-dollar fees**.

### Workflow

1. Verify period unlocked.
2. Run Beast with scoped reservation set.
3. Validate output; check for zero-dollar fee duplication.
4. Provide imbalance report to customer for remaining discrepancies.

### Implementation guidance

- Prefer settings snapshots (Phase 2) over repeated Beast runs for recurring accounts (e.g. Avari).
- Enterprise: white-glove Beast support; SMB: self-service + documentation.

---

## 12. Topic: AI Agent & Settings Snapshots (Roadmap)

### Phase 1 — AI Agent MVP (July 10 release)

| Item | Detail |
|------|--------|
| **Goal** | Convert CSV exports → automated mapping |
| **Release** | July 10, 2026 (confirmed Workshop #2) |
| **Scope** | MVP — not full regional coverage |

**Implementation guidance**

- Product defines CSV input schema and expected mapping outputs.
- Engineering delivers agent pipeline; QA with real account exports.
- Document limitations (no universal import — Section 4).

### Phase 2 — Settings Snapshots

| Item | Detail |
|------|--------|
| **Goal** | Reservation settings as source of truth |
| **Benefit** | Avari maintenance: 5–6 hrs/month → ~30 min |
| **Replaces** | Manual adjustments |

**Implementation guidance**

- Snapshot financial settings at reservation creation.
- Channel updates respect snapshot + override rules (Section 8).
- Rollout after Phase 1 stabilizes.

---

## 13. Topic: Rates & Availability Toggle Removal

### Decision (Workshop #2)

Remove **Rates & Availability feature toggle** from product.

### Gates

1. **Legal review** — Shan (required before removal).
2. **Impact report** — assess accounts still on toggle.

### Implementation guidance

1. Complete legal review with Shan.
2. Publish impact report (accounts affected, migration path).
3. Communicate deprecation timeline to CS and enterprise.
4. Remove toggle in release after approvals.

---

## 14. Topic: Customer Support & Enterprise vs SMB

### Decisions

- **Client owns** financial reconciliation accuracy.
- **Imbalance reports** — not universal migration fixes.
- **Enterprise:** white-glove support for migration and Beast.
- **SMB:** self-service + documentation + imbalance reports.

### Implementation guidance

1. Template imbalance report for CS (fields: reservation ID, channel, PMS value, channel value, tax flag).
2. Escalation path: SMB → CS docs; Enterprise → dedicated CSM + T3 for bulk (BDC 2.0).
3. Do not commit to auto-fix all discrepancies.

---

## 15. Topic: Regional Complexity (Australia, GST)

### Background

Workshop #2 discussed Hometime and Australia GST / tax eligibility — no one-size-fits-all solution.

### Principles

- Regional tax rules override generic mapping templates.
- Channel tax data still source of truth for remittance.
- Product/legal review for edge cases.

### Implementation guidance

1. Document Australia GST exceptions in regional appendix (Confluence).
2. Flag AU accounts in migration checklist.
3. Escalate Hometime-like cases to product + legal before custom mapping.

---

## 16. Implementation Guidance by Phase

### Pre-migration checklist

- [ ] Audit account fee dictionary; apply $1/day workaround where needed
- [ ] Confirm source-of-truth rules with customer (PMS vs channel for fees; channel for taxes)
- [ ] Export sample reservations per channel (BDC, VRBO, Airbnb)
- [ ] Check BDC Deduct 2.0 status
- [ ] Identify enterprise vs SMB support tier

### Migration execution

- [ ] Run reverse mapping with PMS-as-truth for fees
- [ ] Import taxes from channel only — no adjustments
- [ ] Preserve manual overrides
- [ ] Generate imbalance report

### Post-migration

- [ ] Deliver imbalance report to client
- [ ] Client-owned reconciliation
- [ ] Beast only if period unlocked; watch zero-dollar fee bug
- [ ] Log open items for Phase 2 (settings snapshots)

### July 10 release (Phase 1)

- [ ] AI agent CSV → mapping pipeline GA
- [ ] Release notes + limitations doc
- [ ] CS training on new workflow

---

## 17. Action Items & Open Questions

### Action items (from workshops)

| Owner | Action | Workshop |
|-------|--------|----------|
| Product | Finalize default fee dictionary strategy | WS1 O1 |
| Product | Impact report for Rates & Availability toggle | WS2 D11 |
| Shan / Legal | Legal review for toggle removal | WS2 D11 |
| Engineering | AI agent MVP for July 10 | WS2 D9 |
| Engineering | Settings snapshots (Phase 2) | WS2 D10 |
| Engineering | Fix Beast zero-dollar fee duplication | WS2 |
| Ops / T3 | BDC Deduct 2.0 ~2,000 reservations | WS2 |
| Alex / Engineering | Document manual override non-revert behavior | WS1 D6 |

### Open questions

1. System-level fee dictionary for new accounts (WS1 O1)
2. Final financial import discrepancy resolution strategy (WS1 O2) — partially addressed by imbalance reports + client ownership
3. Australia GST / Hometime edge cases — regional playbook needed
4. Beast fix timeline for locked periods and zero-dollar fees

---

## 18. Appendix: Related Links & Source Files

### Source workshop notes (Gemini)

| Workshop | File |
|----------|------|
| #1 — May 20, 2026 | [`docs/workshop-notes/workshop-1-may-20-gemini-notes.txt`](../workshop-notes/workshop-1-may-20-gemini-notes.txt) |
| #2 — May 28, 2026 | [`docs/workshop-notes/workshop-2-may-28-gemini-notes.txt`](../workshop-notes/workshop-2-may-28-gemini-notes.txt) |
| Original `.docx` | [`docs/workshop-notes/`](../workshop-notes/) |

### Internal references

- Slack: `#reverse-mapping-ga`
- Jira: reverse mapping / BDC Deduct 2.0 epics
- Confluence: channel import mapping specs

### Document history

| Date | Change |
|------|--------|
| June 2026 | Initial interim draft (Slack/docs synthesis) |
| June 14, 2026 | Merged Gemini workshop notes #1 and #2; full decision log and topic structure |

---

*This playbook is a living document. Update after each reverse-mapping workshop or major release.*
