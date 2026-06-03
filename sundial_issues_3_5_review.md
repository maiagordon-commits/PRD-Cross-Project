# Sundial Getaways - Issues 3-5 Support and Platform Review

## Executive summary

For Issues 3-5, the customer's frustration is materially justified. Issues 3 and 5 are confirmed platform/API defects, while Issue 4 appears to be expected accounting/reporting behavior but was handled poorly at first because the AI response ignored the customer's explicit request not to ask follow-up questions.

The largest patterns are:

- Real product defects were present in multiple areas: property report email delivery, scheduled report content, and reservations-v3 retrieval.
- Support often responded, but ownership was fragmented and sometimes relied on generic or premature responses.
- Resolution was communicated before the customer's real use case was validated, especially on Issue 3.
- The customer repeatedly supplied detailed evidence, including Loom videos, examples, screenshots, IDs, and request IDs.

## Consolidated timeline summary

| Issue | Created / first report | First human response | Escalation / specialist involvement | Resolution / latest status | Time to first human response | Time to resolution |
|---|---|---|---|---|---|---|
| Issue 3 - Properties reports not delivered / blank | Apr 14, 18:12 | Apr 15, 05:37 | Jira created Apr 15, engineering finding Apr 16 | Not confirmed resolved; later status says bugfix ready and awaiting release | About 11h 25m | Not resolved; latest customer failure was about 23 days 4h after creation |
| Issue 4 - Owners Portal / Analytics discrepancy | Saturday, 00:16 | Sunday, 03:43 | CSM escalation Saturday 00:57; domain specialist analysis Monday 09:44 | Monday 09:54 answer, assuming it fully addressed the Loom | About 27h 27m | About 2 days 9h 38m to final answer |
| Issue 5 - reservations-v3 VRBO retrieval failure | Not included in pasted content | Sunday, 11:03, based on known customer-facing response | Internal validation Sunday 09:47; Jira/pre-triage about May 31 | Not confirmed resolved; escalated to RES | Cannot calculate exactly without created timestamp | Not resolved / not enough data |

## Issue 3 - Properties report emails not delivered / blank

### Timeline and elapsed time

| Metric | Value |
|---|---|
| Created date | Apr 14, 18:12 |
| First human response | Apr 15, 05:37 |
| Time to first human response | About 11h 25m |
| First Jira escalation | Apr 15, 05:31 |
| First engineering finding | Apr 16, 15:52 |
| First "fixed" update to customer | Apr 27, 16:28 |
| Customer reported still broken | Apr 27, 21:28 |
| Second Jira raised | May 1, 02:36 |
| Customer reported still broken again | May 7, 22:26 |
| Latest known engineering status | Bugfix ready and awaiting release |
| True resolution date | Not confirmed |
| Time to resolution | Not resolved / cannot calculate final resolution |
| Time open as of latest customer failure | About 23 days 4h |

### Assessment

| Category | Assessment |
|---|---|
| Customer impact | High. Reporting emails were either not delivered or arrived blank, affecting recurring operational reports. Account was marked high risk / escalated. |
| System/platform issue | Yes. Jira confirms real bugs: first a Nunjucks template rendering failure after Hydra 5, then a later unresolved blank-report bug. |
| Support quality | Mixed to poor. Initial acknowledgement was good, but later replies asked for information already effectively provided and communicated resolution too early. |
| Engineering handling | Slow/incomplete. First bug was fixed, but the customer later proved the use case still failed. A later Jira comment confirmed the bugfix was ready and awaiting release. |
| Current status | Not safe to call resolved unless the release is confirmed and the customer's scheduled reports are populated. |
| Customer complaint justified? | Yes. Both product reliability and support process contributed. |

### Support review

- First response was reasonably timely.
- Support initially understood that the report email was not received.
- Later understanding drifted: the customer clarified that the recurring scheduled report was arriving blank, not that manual sending failed.
- Multiple handoffs occurred across support agents and engineering.
- The customer had to repeat that support already had the evidence.
- Manual test success was incorrectly treated as proof that scheduled recurring reports were fixed.

### Answers to review questions

#### Was the first response timely?

Yes. The customer opened the ticket on Apr 14 at 18:12, and the first human response was Apr 15 at 05:37, about 11h 25m later.

#### Did support understand the issue correctly?

Initially yes, for the first symptom: the report email was not delivered. Later the issue evolved into scheduled recurring reports arriving blank, and support did not consistently distinguish manual report sending from scheduled report delivery.

#### Were answers specific or generic?

Mixed. The first response was specific enough and acknowledged the video. Later replies became repetitive and asked for more information even though the customer had already provided report names, screenshots, examples, and links.

#### Did the ticket get ownership and follow-up?

There was follow-up, but ownership was fragmented across several agents and engineering. No single owner appears to have managed the full customer experience from initial report through verified resolution.

#### Were escalations handled quickly enough?

The first Jira escalation was quick, but resolution was not. Engineering found a global template issue on Apr 16, the customer was told it was fixed on Apr 27, then later May 7 evidence showed the issue still occurred.

#### Did the customer have to repeat themselves?

Yes. The customer explicitly pushed back that support already had everything needed and asked not to be asked for more information.

#### Was the issue actually resolved?

Not confirmed. Apr 27 and May 6 should not be treated as true resolution dates because the customer later reported continued blank reports, and the latest pasted engineering status says the bugfix was ready and awaiting release.

### Full assessment conclusion

The customer complaint is justified. This was not just a misunderstanding or support education issue; it included confirmed platform defects and a weak support process. The biggest support failure was communicating resolution before validating the customer's actual scheduled-report use case.

### Platform findings

There were at least two real issues:

1. No email delivered:
   - Root cause: Nunjucks template syntax error after Hydra 5 upgrade.
   - Impact: global property report email share failure.
   - Evidence: engineering noted 50+ identical worker errors and zero completed logs.
2. Blank recurring reports:
   - Initially treated as resolved/non-issue based on manual test deliveries.
   - Customer later proved it still occurred.
   - Engineering later confirmed it was a bug and the bugfix was awaiting release.

### Recommended next actions

- Confirm whether the latest bugfix has been released.
- Run an internal scheduled-report test for Sundial's exact views: Tuya Lock Health Updates and PCB listings.
- Send the customer one specific update with root cause, fixed scope, release status, and expected next successful scheduled report.
- Assign one named owner for this escalation.
- Do not ask the customer for more examples unless a new failure occurs after the confirmed release.
- Add internal support guidance: manual report delivery success is not enough to close recurring scheduled report issues.

## Issue 4 - Owners Portal / Analytics revenue discrepancy

### Timeline and elapsed time

| Metric | Value |
|---|---|
| Created date | Saturday, 00:16 |
| AI response | Saturday, 00:16 |
| CSM escalation | Saturday, 00:57 |
| First human customer response | Sunday, 03:43 |
| Time to first human response | About 27h 27m |
| Domain specialist internal analysis | Monday, 09:44 |
| Final customer answer | Monday, 09:54 |
| Time to resolution / answer | About 2 days 9h 38m from created date |
| True resolution date | Monday, 09:54, assuming Michelle's answer fully addressed the Loom issue |
| Reopen | None shown |

### Assessment

| Category | Assessment |
|---|---|
| Customer impact | Medium-high. The issue concerns financial reporting, and the customer was already frustrated. |
| System/platform issue | No confirmed bug from the pasted evidence. The discrepancy appears related to comparing Reservation Report data with Accounting-based Analytics/Owner Statement data. |
| Support quality | Mixed. Initial AI response was poor for this customer context; later specialist handling was much better. |
| Engineering handling | No engineering issue shown. This appears to be product/accounting behavior clarification unless the Loom shows a different defect. |
| Current status | Probably answered, but not necessarily de-escalated. |
| Customer complaint justified? | Partially. Platform behavior may be correct, but the support experience was not good. |

### Support review

- The immediate AI response was timely but inappropriate for the customer's message.
- The customer explicitly said all evidence was in the Loom and asked not to be asked additional questions.
- The AI replied that it could not view the Loom and asked several questions, which likely increased frustration.
- Human escalation eventually reached a domain specialist.
- Michelle's response was specific and included monthly financial values and an explanation of Accounting vs Reservation Report logic.

### Answers to review questions

#### Was the first response timely?

Yes, but the first response was from AI and was not helpful in context. The first human customer response came Sunday at 03:43, about 27h 27m after the Saturday 00:16 ticket creation.

#### Did support understand the issue correctly?

Eventually yes. The final human analysis identified that the customer was comparing Analytics / Owners Portal figures with Reservation Report figures while using Guesty Accounting.

#### Were answers specific or generic?

The AI answer was generic and poorly matched to the customer's tone. Michelle's final response was specific and included monthly Owner Revenue and Net Rental Income figures.

#### Did the ticket get ownership and follow-up?

Yes, but with handoffs. The ticket moved from AI to CSM escalation, then to Kiehren, Mauricio, and Michelle. The positive point is that it reached a domain specialist.

#### Were escalations handled quickly enough?

Reasonable for a weekend ticket, but the customer was already high-risk and frustrated. A human should have owned the first external response because the customer explicitly provided a Loom and asked not to answer more questions.

#### Did the customer have to repeat themselves?

No repeat is shown after the AI response, but the AI response asked the customer to restate information that was supposedly in the Loom. That created avoidable friction.

#### Was the issue actually resolved?

Assumed yes only if Michelle's explanation fully matched the Loom example. This should be treated as "answered / explained," not "bug fixed," because no confirmed platform defect is shown in the pasted evidence.

### Full assessment conclusion

The customer's frustration is partially justified. The platform behavior appears explainable by Accounting logic rather than a confirmed defect, but the support experience started poorly because the AI response ignored the customer's explicit instruction and did not account for account-health risk.

### Platform findings

Based on the pasted content, this does not look like a confirmed system defect.

Likely explanation:

- The customer compared Analytics/Owners Portal revenue to Reservation Report figures.
- Because the account uses Guesty Accounting, expenses are reflected in Accounting / Owner Statements, not in the Reservation Report.
- Michelle indicated that Analytics matches Accounting, including expenses.

This may still indicate a UX/documentation gap if the product makes these reports appear directly comparable.

### Recommended next actions

- Have a human owner acknowledge the Loom and apologize for the initial AI response.
- Explain plainly that because the account uses Accounting, Owner Revenue should be validated against Owner Statements / General Ledger, not Reservation Report.
- Confirm that the exact example in the Loom matches Michelle's spreadsheet calculation.
- Share a customer-safe calculation summary if possible.
- Add internal guidance: do not route low-health/escalated customers with Loom-only evidence to an AI-only first response.

## Issue 5 - reservations-v3 cannot retrieve existing VRBO reservation by reservationIds[]

### Timeline and elapsed time

| Metric | Value |
|---|---|
| Created date | Not included in pasted content |
| First known internal validation | Sunday, 09:47 |
| First customer-facing human response | Sunday, 11:03 |
| Time to first human response | Cannot calculate exactly without created timestamp |
| Jira/pre-triage activity | About 3 days before Jun 3, likely May 31 |
| Earliest relevant log evidence | May 25, 18:43-18:46 UTC |
| Reservation creation date | Feb 12, 2026 |
| Resolution date | Not confirmed |
| Time to resolution | Not resolved / cannot calculate final resolution |
| Time defect existed for example reservation | More than 3 months from reservation creation to report |

### Assessment

| Category | Assessment |
|---|---|
| Customer impact | High. The customer relies on webhooks plus reservations-v3 retrieval. The issue blocks reliable API workflows and forces fallback to legacy v2. |
| System/platform issue | Yes. Jira triage confirms a systemic V3 data inconsistency for the VRBO reservation, not user error or timing/race condition. |
| Support quality | Good initial handling. API Support validated the issue, confirmed expected endpoint behavior, escalated to engineering, and gave a temporary fallback. |
| Engineering handling | Still pending from the pasted evidence. RES team needs to fix the endpoint/data inconsistency and documentation. |
| Current status | Escalated, unresolved in pasted evidence. |
| Customer complaint justified? | Yes. The customer correctly identified a likely API bug and provided strong technical evidence. |

### Answers to review questions

#### Was the first response timely?

Likely yes, but exact calculation is blocked because the ticket creation timestamp was not pasted. The first known internal validation was Sunday 09:47, and the first customer-facing response was Sunday 11:03.

#### Did support understand the issue correctly?

Yes. Moshe confirmed that all reservations should be accessible through the same endpoint and that Jira should be opened.

#### Were answers specific or generic?

Specific. The support response:

- Confirmed the issue was validated.
- Stated engineering was asked to assist.
- Provided a workaround: legacy GET /reservations/{id}.

#### Did the ticket get ownership and follow-up?

Initial ownership was good. Moshe explicitly said he would handle opening the Jira ticket. The Jira content includes concrete API calls, request IDs, related ticket RES-5075, and a clear escalation target to RES.

#### Were escalations handled quickly enough?

Initial escalation appears quick. The open risk is engineering resolution speed, because the pasted evidence does not include a fix or ETA.

#### Did the customer have to repeat themselves?

No evidence of that in the pasted content. The customer supplied a clear technical description, and support used it effectively.

### Platform findings

This is a confirmed platform/API issue.

Key facts:

- Webhook emits a valid reservation.updated event with reservation ID.
- GET /reservations-v3?reservationIds[]=698e17868e998b0014c9ccd8 returns an empty array.
- The reservation exists and is not new; it was created Feb 12, 2026.
- The issue appears more related to VRBO/channel reservations.
- ZORI found reservations-v3 group view record missing.
- Logs show: [getGroupReservation] group reservation view not found.
- Inquiries service also could not find the linked inquiry record.
- accounting-v3-bulk-tasks returned a 500 while trying to regenerate the reservation.
- The triage conclusion says this is a systemic V3 data inconsistency, not sync lag or user error.

### Support-service findings

This issue was handled better than Issues 3 and 4:

- Support did not argue with the customer.
- Support validated the bug internally.
- Support escalated to the correct engineering team.
- Support gave a practical fallback endpoint.
- The Jira ticket included strong technical detail and request IDs.

The main gap is lack of confirmed resolution in the provided content.

### Recommended CTO-ready conclusion

For Issue 5, the customer's complaint is justified and technically accurate. The reservations-v3 endpoint failed to retrieve an existing VRBO reservation by reservationIds[], despite webhook delivery and the reservation existing in other Guesty domains. Support handling was comparatively strong: API Support validated the issue, confirmed expected behavior, escalated to engineering, and provided a legacy fallback. The unresolved risk is product/API reliability and whether the RES team has fixed the V3 data inconsistency and documentation.

### Recommended next actions

- Confirm current RES ticket status and owner.
- Confirm whether the linked RES-5075 fix applies to admin/openapi endpoint behavior.
- Regenerate or repair the missing V3 group reservation view for the affected reservation.
- Test the exact API call again:
  - GET /reservations-v3?reservationIds[]=698e17868e998b0014c9ccd8
- Check whether other VRBO reservations for the same account are missing V3 group view records.
- Update documentation if VRBO/channel reservations have any endpoint limitations, though current support understanding says they should not.
- Keep the customer on the fallback GET /reservations/{id} only as a temporary workaround, not as the final answer.

## Cross-issue patterns

| Pattern | Evidence |
|---|---|
| Real platform issues exist | Issue 3 and Issue 5 are confirmed bugs/defects. |
| Customer provides strong evidence | Looms, screenshots, report IDs, reservation IDs, request IDs, and exact endpoints. |
| Support quality is inconsistent | Issue 5 was handled well; Issues 3 and 4 had avoidable support friction. |
| AI/generic replies increase frustration | Issue 4 AI response ignored customer context and asked follow-up questions. |
| Premature resolution is risky | Issue 3 was called fixed before the scheduled-report use case was validated. |
| Need named owner | Fragmented ownership appears in Issues 3 and 4. |

## Recommended account recovery actions

1. Assign one named escalation owner for Sundial Getaways.
2. Send a consolidated update separating:
   - Confirmed bugs.
   - Expected behavior / reporting explanation.
   - Open engineering work.
   - Temporary workarounds.
3. For Issue 3, do not mark resolved until scheduled reports for the exact Sundial views are validated after release.
4. For Issue 4, send a clearer accounting explanation and acknowledge the poor AI first response.
5. For Issue 5, provide RES ticket status, owner, next engineering step, and the temporary v2 fallback.
6. Add internal support note: for this account, avoid AI-only replies and avoid asking for evidence already provided.
