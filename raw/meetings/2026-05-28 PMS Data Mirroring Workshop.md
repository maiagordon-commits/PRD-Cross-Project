# PMS Data Mirroring Workshop 2

Date captured: 2026-06-01
Meeting date: 2026-05-28
Source type: Fellow meeting notes
Source link: https://fellow.link/QWH0FDG5XDC4
Captured by: Cursor agent
Related wiki page: [[../../wiki/processes/PMS Data Mirroring Playbook]]

## Raw Content

Maia shared this as the second workshop on improving the long and difficult process of mirroring old PMS data into Guesty to support accurate financial data.

Participants:
- Maia Gordon
- Alex B, Implementation Manager
- Ella Waldman, Financials Product Director
- Javier, Distribution Product Director
- Rinat, Financials Product Manager

Maia pasted the Fellow AI summary into chat on 2026-06-01. The meeting focused on financial data mapping and migration challenges for OTA integrations, including an AI-powered financial mapping tool, Avari locked-period migration issues, VRBO data-quality problems, Australian tax handling, rates-and-availability behavior, and Avari end-of-month processing.

Key raw points from the pasted summary:
- The financial mapping tool should have two components: intake/mapping and output that creates settings rather than adjustments.
- The tool could reduce monthly adjustment work from 5-6 hours to a shorter guided mapping process.
- Avari had about 1,200 March/April reservations stuck in locked accounting periods needing migration to DeductLogic 2.0 before June 1 owner statements.
- Tier 3/API and BEAST investigation should run in parallel for urgent migration handling.
- Channel fees should remain visible on folios while adjusted fees are applied as background settings.
- Australia has tax complexity because rent is non-taxable while fees are subject to GST.
- Reverse mapping can incorrectly map old-system fees into Guesty fee behavior.
- Rates and availability without the relevant feature toggle can prevent fees from bundling into accommodation fare.
- Avari end-of-month processing should complete before ViewStay due to Wallet transaction-limit concerns.

## Notes for Synthesis

- Important facts: Workshop continued PMS data mirroring and added AI mapping, locked-period migration, channel fee display, Australia tax, rates-and-availability, and Avari EOM topics.
- Potential decisions: Use settings/snapshots rather than recurring adjustments; pursue dual migration path via Tier 3/API and BEAST; keep channel fees visible while applying adjusted settings in background.
- Risks/blockers: BEAST locked-period behavior; urgent Avari owner-statement timing; VRBO low-quality fee/tax data; Australia GST complexity; rates-and-availability liability.
- Action items: Alex to create Tier 3 tickets; Rinat to investigate BEAST and escalate to PM; Ella to connect with Tamar on CSV converter/AI; Javier to report impacted rates-and-availability customers.
- Follow-up questions: Which parts of AI mapping become productized and which stay implementation workflow?

