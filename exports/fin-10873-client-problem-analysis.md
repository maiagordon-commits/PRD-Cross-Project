# FIN-10873 — Client Problem Analysis (Hometime)

**Ticket:** [FIN-10873](https://guesty.atlassian.net/browse/FIN-10873) — *Taxes Line Items Incorrect*  
**Account:** Hometime MRP (`6989bac56844f86a9df2db8c`)  
**Reporter:** Harry Houldsworth  
**Created / Resolved:** 8–9 Jun 2026 · **Resolution:** Bug Fix (Denys Kublytskyi)  
**Related:** [T3-167520](https://guesty.atlassian.net/browse/T3-167520) (EOM blocker → remediations tied to FIN-10873)

---

## Executive summary

FIN-10873 was not an isolated “wrong GST display” ticket. For Hometime, it was the May/June EOM moment where **tax-inclusive + markup-on-fees bugs** made Airbnb folios and balances unreliable — so **owner statements and payouts could not be trusted**. That technical failure landed on top of weeks of eroded confidence (including client pressure to fall back to Resly), which is why the issue felt existential to the client, not just operational.

---

## What the issue was (technical)

### Symptom (what the client / CSM saw)

Harry’s ticket description captured the customer-facing problem clearly:

> Airbnb reservations seem to have an **outstanding balance** — so either payment values or folio line items are wrong. On review, **taxes do not match expected values and are not 10% for the resort fee**.

- Impact spreadsheet (“Flagged discrepancy” tab) listed **51+ reservations**
- Example reservation called out: `6a0ebd434f1fcf00133fa4ef`
- Escalated in Slack as an **EOM / payout blocker** (“customer is wanting to payout tomorrow”)

### Root cause (FIN engineering)

Denys’ fix comment (9 Jun) explained the bug was limited to reservations with **markup on fees + inclusive taxes**:

1. Markup on fees was **extracted on every calculation** and **re-added in the first step**
2. Inclusive taxes were extracted **from that markup**
3. The re-added markup **lacked tax**, so the pre-extraction amount was wrong → resort-fee GST no longer correctly reflected **10%**

**Code fix:** Change markup extraction so markup is extracted from applicable invoice items **only on channel update**, or for automatic invoice items / cleaning fee **on each recalculation** (same pattern as inclusive taxes).  
PR: `financials-v3#1739` — *feat(FIN-10873): Remove unused spreadFeesMarkup logic and tests*.

### Why “closed” still felt broken to the client

| Date | What happened |
|------|----------------|
| **9 Jun** | Code fixed; spreadsheet reservations recalculated; ticket closed Bug Fix |
| **10 Jun** | Harry listed **8 reservation IDs** still wrong (“still have this issue”) — last day of EOM |
| **10 Jun** | Denys: code is fixed; **recovery still needed**. Those IDs weren’t in the impact report because GST already showed 10%. Recommended bulk recalc of **~2,000** Hometime reservations with markup-on-fees + tax-inclusive (checkout after 1 May) |

So the client pain continued after Jira closure because **data recovery lagged the code fix**.

---

## What the problem was *to the client* (frustration lens)

Alvan’s full email body was not available in Slack/Jira as pasted text. What *is* documented is what the client was pushing through that email and EOM escalation — and the partnership context around it.

### What Alvan / Hometime were asking for

From `#hometime-internal` (Harry → Product/FIN, 4–8 Jun):

- Reply to **Alvan’s email** on **queries and reports**
- Ticket Alvan shared ([T3-167520](https://guesty.atlassian.net/browse/T3-167520)): **taxes don’t seem to be 10%** on reservations found during EOM
- Explicit ask: *what can Guesty do to clear tax issues so they have **more confidence***
- Same week: payouts / owner statements blocked — “Owners are waiting for their statements”

### Why that email landed with so much frustration

FIN-10873 was the latest proof point in a longer trust spiral:

1. **Confidence already thin (12 May)** — Harry: *“Frustrations are growing… Adjustments, Taxes and Payments seem to be tripping us up… confidence is starting to wear thin.”*
2. **Partnership risk (19 May)** — Internal decisioning that Hometime had **no confidence**, considering rollback to Gross + **Resly** for tax breakout; Alvan called Yoav that they were moving toward Resly.
3. **EOM is non-negotiable** — Wrong resort-fee GST → outstanding balances → statements/payouts unsafe. Harry: *“Tickets above get us to EOM”* / *“customer is wanting to payout tomorrow.”*
4. **Fix without full recovery feels like a broken promise** — Ticket closed 9 Jun; on 10 Jun (last EOM day) multiple reservations still wrong, requiring ~2,000-res bulk recalc guidance.

### Client problem in one sentence

> **“We cannot pay owners with confidence because Guesty’s tax-inclusive + markup-on-fees logic is corrupting folio GST (not 10% on resort fees), leaving balances wrong at EOM — and even after a ‘fix,’ we still don’t trust the data until everything is recovered.”**

---

## Combined analysis: ticket vs. client experience

| Layer | Ticket view (FIN-10873) | Client experience |
|-------|-------------------------|-------------------|
| **Problem framing** | Incorrect tax line items on Airbnb res with markup + tax-inclusive | Owner payout / statement integrity is broken |
| **Scope** | Spreadsheet of 51+ flagged res; bug class ~2,000 res | “How many more are wrong that we haven’t found?” |
| **Success criteria** | Code fix + recalculate known IDs | **Confidence** that reports/queries are clean and payouts are safe |
| **Timeline pressure** | Closed in ~1 day (Bug Fix) | Last day of EOM; residual broken IDs after closure |
| **Emotional load** | Support ticket / engineering defect | Weeks of tax/payment friction → Resly consideration → EOM crisis |

---

## Timeline (condensed)

| When | Event |
|------|--------|
| Mid-May | Tax/payment friction builds; “frustrations growing,” confidence wearing thin |
| ~19 May | Alvan / Hometime push toward Resly; Guesty discusses Gross rollback |
| 4 Jun | Alvan email in play (reply requested); related tax-balance tickets (e.g. FIN-10855) |
| 8 Jun | **FIN-10873** + **T3-167520** opened — incorrect taxes block EOM |
| 9 Jun | Root cause fixed; spreadsheet res recalculated; closed Bug Fix |
| 10 Jun | Residual broken reservations; payout urgency; bulk recovery of ~2,000 res recommended |

---

## Takeaways

1. **Root cause was real and specific:** markup-on-fees extraction interacting incorrectly with inclusive tax extraction, breaking resort-fee GST (not 10%) and creating outstanding balances.
2. **Client impact was EOM-critical:** blocked owner statements/payouts on MRP, not a cosmetic folio issue.
3. **Frustration was cumulative:** Alvan’s email sat on top of May confidence loss and Resly pressure — FIN-10873 confirmed the fear that tax data still couldn’t be trusted.
4. **Closure ≠ client resolution:** code fix on 9 Jun still left recovery work; residual IDs on 10 Jun (last EOM day) prolonged the trust problem.

---

## Sources

- [FIN-10873](https://guesty.atlassian.net/browse/FIN-10873) — description, Denys fix comment, Harry residual IDs, recovery guidance  
- [T3-167520](https://guesty.atlassian.net/browse/T3-167520) — EOM tax blocker escalated from Alvan’s findings  
- Slack `#hometown-internal` — Harry/Alex threads on Alvan email, payout urgency, confidence/Resly  
- [Hometime EOM May 2026 Friction Dashboard](https://guesty.slack.com/docs/T4MD2AKN2/F0BGL70AP8B)  
- Impact sheet referenced on ticket: [Flagged discrepancy spreadsheet](https://docs.google.com/spreadsheets/d/1oJuoivqpCAeNwCpo-annPnScXVJecQZiDBX7ZtjACxk/edit?usp=sharing)

*Note: Atlassian MCP was not authenticated in this environment; Jira detail was reconstructed from prior authenticated extraction + Slack. Alvan’s email body itself was not available as full text — client frustration is synthesized from documented asks and surrounding partnership context.*
