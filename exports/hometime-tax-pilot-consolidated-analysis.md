# Hometime Tax Pilot — Consolidated Issue Analysis

**Slack Canvas:** https://guesty.slack.com/docs/T4MD2AKN2/F0BJL8EXAMPLE  
*(URL updated after canvas create)*

Consolidated view: timeline, breakpoint at each touchpoint, and Guesty Product framing (pilot + believed-resolved root cause from early May).

---

## Guesty Product perspective

From a Product lens, the **core tax-inclusive root causes** that had been driving earlier friction were treated as **resolved beginning of May**. Hometime was a **pilot / early account** on tax-inclusive (and related fee/markup behaviours).

That means:
- They were among the first real, high-volume ANZ EOM users exercising the full path (channels → folio → accounting → owner statements → payout)
- Edge cases and combination bugs surface in production EOM use
- Client-found issues in this window are **part of the piloting concept**

That does **not** mean the EOM experience was acceptable — it means the *pattern* of discovery is expected in a pilot, and Guesty’s obligation is fast root-cause + recovery + honest “fixed vs recovering” communication.

| Layer | Product reading |
|-------|-----------------|
| Early May | Primary tax-inclusive root causes believed resolved |
| Late May → June | Pilot under May EOM load surfaces residual / edge / combination bugs |
| FIN-10873 | Specific combination bug: markup on fees + inclusive tax |
| Client frustration | Valid operationally — and the signal the pilot is designed to produce |

---

## Timeline — breakpoint at each touchpoint

| Date | Touchpoint | Breakpoint | Product lens |
|------|------------|------------|--------------|
| Early May | Product baseline | Believed root causes resolved; pilot continues under real EOM load | Baseline assumption the client will test |
| 28 May | Missing extracted taxes (43 confirmed) | “Future fixed” claim fails against late-May bookings | Classic post-fix residual / listing-pattern find |
| 2 Jun | Query “all clear” | Detection overconfidence — client falsifies same day (`HM22EC9R8Y`) | Pilot stress-tests impact queries, not only calc logic |
| 3 Jun | Partial recovery (38/37) | Loop works only after client forces re-open | Correct pilot loop when executed |
| 4 Jun | Wrong GST / reporting gap | Second defect class + no Guesty discrepancy surfacing | Combination path + Product instrumentation gap |
| 9–10 Jun | FIN-10873 / payout | Code fixed but recovery + cash/commission still block EOM | Combination bug + recovery lag |
| 25 Jun | Post-EOM residuals | Client still auditing platform accuracy | Long-tail pilot finds; Guesty should own detection |

---

## How Product should frame this internally

1. May root-cause close was real for known bugs — not the end of combination/edge risk for a pilot under EOM.
2. Hometime finding issues is the pilot working — high-signal finance-grade QA.
3. Where Guesty underperformed the pilot model: declaring “clean” without hermetic detection; lagging recovery; leaving discrepancy reporting to the client.
4. FIN-10873 = pilot-exposed combination bug (markup on fees × inclusive tax), fixed mid-June; EOM recovery was the hard part.
5. Empathy + Product truth: cascade of residual pilot defects at owner-payout time — respond with faster detection and clearer “fixed vs recovering.”
