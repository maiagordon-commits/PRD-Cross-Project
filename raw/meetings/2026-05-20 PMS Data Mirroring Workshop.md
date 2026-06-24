# PMS Data Mirroring Workshop 1

Date captured: 2026-06-01
Meeting date: 2026-05-20
Source type: Fellow meeting notes
Source link: https://fellow.link/NHN1S8ZSXE6H
Captured by: Cursor agent
Related wiki page: [[../../wiki/processes/PMS Data Mirroring Playbook]]

## Raw Content

Maia shared this as the first workshop on improving the long and difficult process of mirroring old PMS data into Guesty to support accurate financial data.

Participants:
- Maia Gordon
- Alex B, Implementation Manager
- Ella Waldman, Financials Product Director
- Javier, Distribution Product Director

Maia pasted the Fellow AI summary into chat on 2026-06-01. The meeting focused on financial reconciliation challenges when migrating customers from legacy PMS systems to Guesty, with deep analysis of OTA data integration issues across Airbnb, VRBO, Booking.com, Vacasa, and Track PMS.

Key raw points from the pasted summary:
- Financial reconciliation should mirror the old PMS for migration reconciliation, not channel data, when matching customer expectations.
- Channel data remains the source of truth for Guesty imports.
- Host payout discrepancies between legacy systems and channels are the customer's responsibility to resolve.
- Rent adjustments should mirror the source system when fees are bundled, with realization dates aligned to customer revenue-recognition method.
- Manual adjustments persisted through two months of testing across channel update scenarios.
- VRBO sends lumped tax instead of granular breakdown, requiring manual tax reconstruction.
- Default fee configuration and reverse-mapping behavior are critical gaps for imported reservations.
- Cleaning fee imbalances can come from bundled linen fees, length-of-stay pricing, or seasonal internal PMS logic.
- Track PMS and some Vacasa examples have severe data-quality or host-payout definition mismatches.

## Notes for Synthesis

- Important facts: Workshop focused on PMS data mirroring into Guesty for accurate financial data across Airbnb, VRBO, Booking.com, Vacasa, and Track PMS scenarios.
- Potential decisions: Mirror old PMS for financial reconciliation; keep channel data as Guesty import source of truth; customer owns irreconcilable host payout discrepancies; schedule follow-up workshop.
- Risks/blockers: VRBO lumped tax data; reverse mapping gap; default fee setup gap; legal/compliance risk from tax discrepancies; unreliable legacy PMS data.
- Action items: Javier to reopen VRBO tax discussion and message Erpal team; Rinat to document reverse-mapping/default-fee gaps.
- Follow-up questions: Which channel-specific behaviors should become product requirements versus implementation-only playbook steps?

