---
title: PMS Data Mirroring Playbook
area: Project Management
workstream: Channels and Financials
type: process
status: active
owner: Maia Gordon
last_updated: 2026-06-01
source_count: 2
tags: [pms-data-mirroring, channels, financials, implementation, playbook]
---

# PMS Data Mirroring Playbook
> This playbook combines two internal workshops on improving how old PMS data is mirrored into Guesty so migrated customers can get accurate financial data.

## Summary
Migrating enterprise customers from legacy PMS systems to Guesty creates financial reconciliation gaps because OTA data, legacy PMS data, and Guesty accounting configuration often represent fees, taxes, rent, and host payout differently. The workshops aligned on a practical operating model: keep channel data as the source of truth for Guesty imports, mirror the old PMS for financial reconciliation where needed, and use controlled mapping/settings-based approaches to avoid endless manual adjustment cycles.

The playbook is organized by channel and cross-channel process areas so Product, Financials, Distribution, and Implementation can see the use case, pain point, current state, current solution, potential solution, and assumptions.

## Key Facts
- Use case: improve the long and difficult process of mirroring old PMS data into Guesty so financial data is accurate.
- Workshop 1 date: 2026-05-20.
- Workshop 1 participants: Maia Gordon, Alex B, Ella Waldman, and Javier.
- Workshop 2 date: 2026-05-28.
- Workshop 2 participants: Maia Gordon, Alex B, Ella Waldman, Javier, and Rinat.
- Stakeholder roles represented:
  - Implementation: Alex B, Implementation Manager.
  - Financials Product: Ella Waldman, Financials Product Director; Rinat, Financials Product Manager.
  - Distribution Product: Javier, Distribution Product Director.
- Channels discussed: Airbnb, VRBO, and Booking.com.
- Legacy/source systems discussed: Vacasa, Track PMS, Streamline, Casa, LiveRes, Escapia Track, ViewStay, and Hometime/Avari migration examples.
- This work is mainly relevant to enterprise / white-glove migrations, not standard SMB onboarding.

## Current Status
- Source links are preserved in `raw/meetings/`.
- Workshop summaries have been synthesized into this playbook.
- Product-facing details still need validation by Financials, Distribution, and Implementation before this becomes an official operating playbook.

## Workshop Sources
| Date | Workshop | Participants | Source |
|------|----------|--------------|--------|
| 2026-05-20 | PMS Data Mirroring Workshop 1 | Maia Gordon; Alex B; Ella Waldman; Javier | [Fellow notes](https://fellow.link/NHN1S8ZSXE6H) |
| 2026-05-28 | PMS Data Mirroring Workshop 2 | Maia Gordon; Alex B; Ella Waldman; Javier; Rinat | [Fellow notes](https://fellow.link/QWH0FDG5XDC4) |

## Playbook Goal
Create a repeatable per-channel view that answers:
- What is the discussed use case?
- What is the current pain point?
- What does each channel currently have related to this pain point?
- What is the current solution?
- What is the potential solution?
- What assumptions must be validated?

## Executive Takeaways
- Guesty should import from channels as the operational source of truth, but migration reconciliation should mirror the old PMS where customers expect historical financial continuity.
- Host payout mismatches between old PMS and channels should be surfaced to customers instead of silently reconciled by Guesty when the source systems disagree.
- Manual adjustments appear to persist through tested channel updates, which makes bulk reconciliation possible, but the team still needs a clear list of update types that can override adjustments.
- A settings/snapshot-based financial mapping tool is the preferred direction because it could reduce repeated monthly adjustment work and avoid override loops.
- VRBO tax data and channel/PMS fee quality remain major blockers.
- Default fee setup or import-specific mapping logic is needed to prevent unrecognized imported fees from breaking accounting mappings.
- Regional tax rules, especially Australia/APAC and EMEA, make a single global solution risky without explicit assumptions and validation.

## Confirmed Decisions
| Date | Decision | Impact |
|------|----------|--------|
| 2026-05-20 | Financial reconciliation for migrations should mirror the old PMS, not channel data, when the goal is matching customer expectations from the legacy system. | Implementation can reconcile against legacy financial reports while Guesty still imports channel data. |
| 2026-05-20 | Channel data remains the source of truth for Guesty imports. | Guesty should not invent imported channel financial data from legacy PMS values. |
| 2026-05-20 | Host payout discrepancies between legacy systems and channels are the customer's responsibility to resolve. | Implementation should provide an imbalance report rather than force a reconciliation when source data disagrees. |
| 2026-05-20 | When fees are bundled into rent, rent adjustments should mirror the source system and realization dates should align with the customer's revenue-recognition method. | Reconciliation must include accounting-date handling, not only amount matching. |
| 2026-05-28 | The financial mapping tool should have intake/mapping and output/settings components. | Product direction favors creating settings or setting snapshots rather than ongoing adjustments. |
| 2026-05-28 | Channel fees should remain visible on folios while adjusted fees are applied as settings in the background. | Preserves channel source-of-truth visibility while making financial output usable. |

## Channel Playbook Matrix
| Channel | Discussed Use Case | Current Pain Point | What This Channel Currently Has | Current Solution | Potential Solution | Assumptions | Source |
|---------|--------------------|--------------------|----------------------------------|------------------|--------------------|-------------|--------|
| Airbnb | Import and reconcile reservations where fees, taxes, rent, and cleaning fees from the old PMS do not match the Airbnb/Guesty view. | Legacy systems may bundle fees into rent or calculate cleaning fees differently from Airbnb, which creates rent, cleaning fee, tax, and host payout deltas. | Airbnb data is treated as channel source of truth; Airbnb can send multiple tax types and fee details, but tax settings may not always be sent when tax was calculated as part of net rent. | Compare legacy PMS reports to Guesty/channel data; adjust rent or cleaning fees to mirror the old PMS where needed; use Toolkit/Gemini-assisted bulk invoice-item creation for large batches. | Move toward a mapping/settings approach that creates reservation-level financial settings or snapshots, keeps channel data visible, and reduces recurring manual adjustments. | Manual adjustments continue to persist through tested Airbnb updates; imported reservation settings can safely become the future source for financial calculations; source records are available to calculate deltas. | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H), [Workshop 2](https://fellow.link/QWH0FDG5XDC4) |
| VRBO | Import and reconcile reservations where bundled fees and tax breakdowns are needed for accurate financial reporting. | VRBO sends lumped tax instead of granular tax breakdowns, and some VRBO data is polluted by incorrect PMS/channel-manager data, creating excessive or zero-value invoice items. | VRBO is strong on bundled-fee setup and can support proper bundled-fee behavior, but current reservation data can include a single tax bucket or many low-quality fee lines. | Zero out VRBO tax and manually re-add tax types according to customer specifications; escalate granular tax breakdown needs with VRBO. | Re-engage VRBO for granular tax transmission and/or initial reservation breakdowns; preserve channel fee visibility while applying adjusted settings in the background. | VRBO has the underlying data needed for better breakdowns; VRBO can provide a cleaner data contract; Guesty can keep channel fee visibility without compromising reconciled financial output. | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H), [Workshop 2](https://fellow.link/QWH0FDG5XDC4) |
| Booking.com | Reconcile imported reservations where taxes and fees do not map cleanly, especially in markets where taxes apply to fees. | Booking.com does not support all Guesty fee/tax rules; bundled fees can inflate accommodation fare and make tax percentages look wrong after fee deduction. | Booking.com may bundle fees into rent and has limitations around tax/fee rule support, especially in Australia/New Zealand where taxes must apply on top of all fees. | Investigate deltas during reconciliation and adjust imported financials manually where needed. | Define import mapping rules that let customers override how taxes/fees are treated on import; validate region-specific rules before applying global behavior. | Booking.com limitations cannot be solved only inside Guesty; regional tax handling needs explicit configuration; import mapping can reduce ongoing manual reconciliation. | [Workshop 1](https://fellow.link/NHN1S8ZSXE6H), [Workshop 2](https://fellow.link/QWH0FDG5XDC4) |

## Detailed Playbook by Area

### 1. Financial Reconciliation Methodology

#### Discussed use case
During enterprise migrations, Implementation needs to compare the old PMS and Guesty/channel data and make Guesty financials match what the customer expects from their legacy PMS reporting.

#### Current pain point
- Legacy PMS systems and channels represent rent, fees, taxes, and host payout differently.
- Some legacy systems create values that do not match channel data, especially Track PMS and some Vacasa cases.
- Customers expect financial continuity, even when the channel and old PMS disagree.
- Realization dates and revenue recognition rules add accounting friction beyond simple amount matching.

#### What currently exists
- Reconciliation compares legacy PMS reports against Guesty/channel reservation data.
- Three primary use cases were identified:
  - total host payout discrepancies,
  - fees bundled into rent,
  - cleaning fee imbalances.
- Alex's team uses a create-invoice Toolkit and a Gemini-assisted workflow to generate bulk invoice items from reconciliation sheets.

#### Current solution
- Use channel data as the source of truth for Guesty imports.
- Mirror the old PMS for financial reconciliation when the customer needs legacy-system continuity.
- For bundled fees, adjust rent to match the source system.
- For cleaning fee imbalances, adjust cleaning fees if source records can identify the delta.
- For host payout mismatches that do not make sense, provide an imbalance report and ask the customer to resolve or advise.

#### Potential solution
- Build a financial mapping tool with:
  - intake templates per competitor/PMS,
  - assisted mapping with knowledgeable implementation leads,
  - output that creates settings or setting snapshots on reservations rather than recurring adjustments.
- Treat mapped imported reservations like regular reservations with settings so future alterations update accommodation fare while preserving mapped fee logic.

#### Assumptions
- Enterprise customers need white-glove reconciliation; SMBs may continue with "what comes from the channel is what you get."
- Old PMS financial continuity matters for customer acceptance even when the old PMS is not technically correct.
- Manual adjustment persistence needs final validation across all relevant channel update scenarios.

### 2. Fee Setup and Imported Reservation Accounting

#### Discussed use case
Prevent imported reservations from creating unrecognized fees or journal-entry/accounting issues when fee settings are missing during onboarding.

#### Current pain point
- Reservations may import before fee setup is complete.
- Imported fees can be reverse-mapped to default Guesty fee types that do not exist in the customer's configured business model.
- This creates accounting confusion, advanced deposit issues, and unexpected folio behavior.

#### What currently exists
- Implementation sometimes creates a $1 per-stay fee for every fee type before imports to avoid unrecognized journal entries.
- A mini-toolkit exists to batch-create these $1 fees at account level.
- Hometime and similar cases showed resort fees or old-system fees mapped incorrectly when setup was incomplete.

#### Current solution
- Pre-create fee settings broadly before importing reservations.
- Use batch tooling to reduce the manual setup cost.
- Document reverse-mapping gaps for imported reservations.

#### Potential solution
- Add default fee configuration at account creation for relevant onboarding flows.
- Add imported-reservation-specific accounting logic or an imported flag.
- Create import mapping rules that let customers or implementation define how incoming fees/taxes should map before they hit accounting.

#### Assumptions
- Default fee setup is safer for complex enterprise migrations than relying on users to configure every fee manually.
- A one-size default may be risky for single-market accounts with uniform fee structures.
- Product needs to decide whether this is an accounting behavior change, an import behavior change, or both.

### 3. Tax Handling

#### Discussed use case
Handle tax discrepancies where channels, legacy PMS systems, and Guesty have different tax structures, especially across APAC, EMEA, and US rules.

#### Current pain point
- VRBO sends lumped tax instead of granular tax breakdowns.
- Airbnb can send multiple tax types, but the team may only know the total imbalance and not the correct proportional allocation.
- Booking.com may not support all fee/tax rules.
- Australia has special handling where rent is non-taxable but fees are subject to GST.
- Tax discrepancies can create legal and compliance risk for property managers.

#### What currently exists
- For VRBO, Implementation zeros out tax and manually re-adds the expected tax types.
- For Airbnb multiple tax types, the team may adjust the larger tax item when allocation cannot be determined.
- Guesty extracts taxes based on local settings for some imported Airbnb reservations when tax settings cannot be pushed through third-party tools.

#### Current solution
- Handle tax corrections manually during enterprise reconciliation.
- Escalate VRBO tax-breakdown limitations.
- Use local settings and tax-inclusive logic where applicable.

#### Potential solution
- Push VRBO for granular tax breakdowns or cleaner initial reservation breakdowns.
- Define import mapping rules for taxes and fees by channel and region.
- Add validation rules for high-risk regions before applying bulk reconciliation.

#### Assumptions
- Tax handling cannot be fully standardized across regions.
- Product and legal/compliance input is needed before changing tax behavior.
- Tax deltas should be transparent to customers when Guesty cannot infer correct allocation.

### 4. Manual Adjustments vs Settings-Based Mapping

#### Discussed use case
Reduce recurring monthly reconciliation by replacing repeated manual adjustments with a mapping/settings approach.

#### Current pain point
- Avari currently requires 5-6 hours of monthly adjustment work.
- Manual adjustments may appear fragile because stakeholders worry channel updates could override them.
- If recurring reconciliation continues monthly, implementation effort does not scale.

#### What currently exists
- Alex tested multiple scenarios over two months, including ARCs, payment webhooks, date changes, Resolution Center updates, and future check-ins.
- In tested scenarios, channel updates did not override manual adjustments.
- Bulk adjustments may be possible for 6-8 months of data if override behavior is understood.

#### Current solution
- Use bulk adjustments and Toolkit where the team has confidence.
- Continue tracking override scenarios manually.

#### Potential solution
- Create settings or setting snapshots during import/mapping so adjusted fees become part of reservation configuration instead of post-import adjustments.
- Preserve channel fees on folios while applying adjusted settings behind the scenes.
- Use AI-assisted mapping to reduce mapping time from hours to a shorter guided workflow.

#### Assumptions
- Settings-based output avoids the "endless override loop."
- Channel alterations can update accommodation fare proportionally while preserving mapped fee calculations.
- Product must define which future updates are allowed to override mapped settings.

### 5. Legacy PMS and Customer-Specific Migration Handling

#### Discussed use case
Understand how competitor systems calculate financial fields so Guesty can map or reconcile migration data correctly.

#### Current pain point
- Track PMS and similar systems may generate unreliable or internally derived financial data.
- Vacasa internal logic can produce cleaning fee or host payout values that do not match Airbnb/channel data.
- Host payout definitions vary by system.

#### What currently exists
- Track migrations may require asking customers what values they want rather than attempting deterministic reconciliation.
- Vacasa reconciliation can work for most reservations, but a meaningful minority require customer input.
- AI-based mapping cannot work until the system understands how each legacy PMS calculates host payout and fees.

#### Current solution
- Reconcile what can be matched.
- Flag irreconcilable host payout discrepancies for the customer.
- Use reports to show customers where the old PMS and channel disagree.

#### Potential solution
- Build competitor-specific intake templates for Streamline, Casa, LiveRes, Escapia Track, Track PMS, Vacasa, and other high-volume systems.
- Bring experienced implementation leads into mapping sessions.
- Use AI to learn fee structures and generate proposed settings/snapshots.

#### Assumptions
- Competitor-specific mapping is required; one generic mapping model will not be enough.
- Customer confirmation is required when source systems disagree materially.

### 6. Avari / Hometime Operational Lessons

#### Discussed use case
Use current migration incidents to shape the product and implementation playbook.

#### Current pain point
- Avari had 1,200 March/April reservations stuck in locked accounting periods needing migration to DeductLogic 2.0 before owner statements.
- BEAST migration tools may not override locked periods as expected.
- Hometime had imported fee and reverse-mapping issues, including fees from old systems mapping into unexpected Guesty fee behavior.
- Rates and availability feature-toggle behavior can affect whether fees are bundled into accommodation fare.

#### What currently exists
- Avari has a process to record payments and an API path to mark payments if needed with written approval.
- Avari end-of-month processing should complete before ViewStay processing to avoid Wallet transaction-limit issues.
- A report is needed for customers using rates and availability without the feature toggle enabled.

#### Current solution
- Use a dual path for urgent migrations: Tier 3 via API and Product/Financials validation of BEAST capability.
- Coordinate Rinat, Autumn, Alex, Jordan, and Tier 3 for locked-period issues.
- Keep Avari and ViewStay sequencing explicit for end-of-month processing.

#### Potential solution
- Fix or document BEAST locked-period limitations.
- Define when API override is acceptable.
- Produce a rates-and-availability impact report before changing default behavior or customer communications.

#### Assumptions
- Locked-period overrides require careful accounting control.
- Customer written approval may be required for bulk payment marking because of bank reconciliation impact.
- Legal review may be needed before broad customer communication about rates-and-availability behavior.

## Product / Process Recommendations
1. **Create official import mapping rules.** Support per-channel and per-region choices for fees, taxes, VAT/GST, bundled fees, and accommodation fare.
2. **Design the financial mapping tool around settings, not recurring adjustments.** The output should create reservation settings/snapshots that survive future alterations.
3. **Preserve channel source-of-truth visibility.** Keep channel fee lines visible on folios while using mapped settings for reconciled financial output.
4. **Define enterprise-only reconciliation scope.** Make clear which services are white-glove enterprise migration support and which are not included for SMBs.
5. **Build competitor-specific templates.** Start with Track/Escapia Track, Vacasa, Streamline, Casa, and LiveRes.
6. **Clarify tax ownership and compliance rules.** Tax allocation should not be guessed when channels provide insufficient detail.
7. **Document override behavior.** Product/Engineering should identify which channel updates can override manual or mapped financial settings.
8. **Create reports before changing rates-and-availability behavior.** Identify impacted customers and legal/commercial risk first.

## Action Items
| Action Item | Owner | Due Date / Timing | Status | Source |
|-------------|-------|-------------------|--------|--------|
| Re-open conversation with VRBO about tax data transmission and push for granular tax breakdown instead of lump sum. | Javier Ibarz |  | Open | Workshop 1 |
| Message / escalate to the Erpal team about VRBO tax data impact on Guesty's reconciliation process. | Javier Ibarz |  | Open | Workshop 1 |
| Document reverse mapping not applying cleanly to imported reservations and the default-fee behavior gap. | Rinat Elimelech |  | Open | Workshop 1 |
| Create Tier 3 ticket to migrate 1,200 March/April Avari reservations to DeductLogic 2.0 via API. | Alex Borack | End of day after Workshop 2 | Open / verify externally | Workshop 2 |
| Coordinate with Autumn and Alex on BEAST not overriding locked periods. | Rinat Elimelech |  | Open / verify externally | Workshop 2 |
| Create Tier 3 ticket to override locked periods and zero out zero-amount invoice items for Hometime migration; coordinate with Jordan if needed. | Alex Borack |  | Open / verify externally | Workshop 2 |
| Escalate BEAST migration tooling issue to Product Management. | Rinat Elimelech |  | Open | Workshop 2 |
| Connect with Tamar to review the CSV converter tool with AI and assess expansion for competitor mapping. | Ella Waldman |  | Open | Workshop 2 |
| Create report of customers using rates and availability without the feature toggle enabled and impacted by fees not bundled into accommodation fare. | Javier Ibarz |  | Open | Workshop 2 |

## Risks / Blockers to Watch
| Risk / Blocker | Impact | Owner / Function | Mitigation / Next Step |
|----------------|--------|------------------|------------------------|
| VRBO provides lumped tax and low-quality fee/tax data. | Manual tax reconstruction remains expensive and risky. | Distribution / Javier | Push VRBO for granular tax breakdown and cleaner initial reservation data. |
| Legacy PMS data is unreliable or internally derived. | Guesty cannot safely reconcile without customer input. | Implementation | Provide discrepancy reports and get customer guidance. |
| Imported fees reverse-map to incorrect Guesty fee settings. | Accounting mappings and owner statements can be wrong. | Financials Product | Define imported-reservation mapping behavior and default fee setup. |
| Regional tax rules differ materially. | Global import behavior could create compliance risk. | Financials / Legal / Product | Validate APAC, EMEA, US handling separately. |
| Manual adjustments may be overridden by unknown future events. | Bulk reconciliation may be unsafe if override cases are missed. | Product / Engineering | Publish tested and untested channel update scenarios. |
| BEAST tools may not override locked periods. | Avari/Hometime migrations can miss owner-statement deadlines. | Financials Product / Tier 3 | Validate tool behavior and define API fallback. |
| Rates-and-availability behavior affects customer revenue expectations. | Release notes or product changes may trigger compensation/liability concerns. | Distribution / Legal / Product | Produce impact report and legal review before rollout. |

## Open Questions / Gaps
- Which parts of this playbook should become product requirements versus implementation process?
- Which imported-reservation events are guaranteed not to override mapped settings or manual adjustments?
- What is the official source-of-truth policy when old PMS, OTA, and Guesty disagree?
- Which competitor PMS templates should be prioritized first?
- What minimum fields are required in the intake template for AI-assisted financial mapping?
- Should default fee setup be enabled for all enterprise migration accounts or only selected migration profiles?
- What approval is required before Guesty bulk-marks payments or overrides locked accounting periods?
- What customer-facing language is needed for rates-and-availability limitations?

## Suggested Share Title
**PMS Data Mirroring Playbook: OTA Reverse Engineering for Accurate Financial Migration Data**

## Related Pages
- [[Processes]]
- [[../meetings/Meetings]]
- [[../projects/Distribution Project]]
- [[../risks/Risk Register]]
- [[../dependencies/Dependencies]]
- [[../decisions/Decision Log]]

## Source Log
| Date | Source | What was added |
|------|--------|----------------|
| 2026-06-01 | [PMS Data Mirroring Workshop 1](https://fellow.link/NHN1S8ZSXE6H) | Captured meeting metadata, participants, use case, and playbook need. |
| 2026-06-01 | [PMS Data Mirroring Workshop 2](https://fellow.link/QWH0FDG5XDC4) | Captured meeting metadata, additional participant, use case, and playbook need. |
| 2026-06-01 | User-pasted Fellow summaries | Synthesized detailed combined playbook, decisions, channel matrix, action items, risks, and recommendations. |

