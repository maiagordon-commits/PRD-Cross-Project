# Hometime Tax Emails — Timeline & What Went Wrong

**Source:** Client email thread *Tax Missing Reservation List* (Alvan Aiau Yong / Ching Lim ↔ Harry / Alex), PDF forwarded 20 Jul 2026.  
**Slack Canvas:** https://guesty.slack.com/docs/T4MD2AKN2/F0BJE02T078

---

## Bottom line

This was not one FIN-10873 incident. Over ~4 weeks (28 May–25 Jun), Hometime kept finding tax, folio, and accounting errors that Guesty’s queries missed or only partially fixed — blocking EOM confidence and owner payouts. FIN-10873 (markup-on-fees × inclusive tax) was one peak in a longer cascade.

**Client problem in one line:** They could not trust Guesty tax/folio/accounting data enough to run owner statements and payouts without doing their own audit every few days.

---

## Issues that went wrong (by type)

| # | Issue | What it did to the client |
|---|--------|---------------------------|
| 1 | Missing `extractedInclusiveTaxes` | Taxes couldn’t export cleanly to accounting; Alvan counted **43 confirmed** (MRP 30 / TBC 13) |
| 2 | Whitesands / BDC Rates & Availability FT bug | Fees not bundled into AF → **negative accommodation fare** on Villa 1 & 3 |
| 3 | Detection / query blind spots | Guesty said “clean”; query missed `$0.00` tax; client kept finding broken res |
| 4 | FIN-10873 — markup on fees × inclusive tax | GST calculated wrong → unreconciled balances at May EOM |
| 5 | Cash / Advanced deposit recognition | Payments not in accounting; GST stranded in Advanced deposit |
| 6 | Post-EOM residuals (25 Jun) | VRBO GST stripped; BDC GST+VAT double-count; GST rounding 15.46 vs 15.45 |

---

## Timeline

### 28 May — Wave 1: missing extracted taxes

Harry shares initial MRP/TBC review list.

**Alvan’s analysis:**
- **43 confirmed** missing tax breakdown
- Channels: BDC 24 ($19.8k) · Airbnb 9 ($21.5k) · Direct 6 ($33.6k) · VRBO 3 · Stayz 1
- **84%** checkout May/Jun — must fix before owner statements
- Guesty said future-res fixed — **false**: bookings still created **26–27 May**
- Whitesands pattern: 16/23 recent = Villa 1/3 + Clean Fee + consumable + markups on fees

**Asks:** root cause of late May bookings; when did fix ship; remediation plan for 43; Whitesands config needs.

### 2 Jun — Trust break: “all clear” was wrong

- **Alvan (urgent):** promised overnight list not received — needs clarity before surfacing **owner revenue in the portal**
- **Harry:** query missed `$0.00` (looked for `-`); claims re-query now returns zero; explains Whitesands FT bug + Yoav compensation
- **Alvan (same morning):** `BC-62F3FF509` fixed, but `HM22EC9R8Y` still broken — **contradicts** “no reservations requiring correction”

### 3 Jun — Partial recovery

Harry: query adjusted → **38 found, 37 fixed**, 1 left (`DBBF2A108B67`). Alvan will validate; still waiting Whitesands impact / Yoav proposal.

### 4 Jun — Wave 2: GST calculated wrong (→ FIN-10873)

- **Alvan (MRP EOM, May 1–30):** GST now included but **calculated incorrectly** on many reservations
- **Harry:** tax **added instead of extracted** → overpaid; ticket for Alex
- **Alvan:** wants root cause; Guesty still lacks reporting to catch tax discrepancies vs channels (he finds them with MCP) — **“quite disappointing”**

### 9–10 Jun — EOM crisis / FIN-10873

- **Alvan:** update on outstanding tax list? Ching flagged **“Markup on fees” affected by GST bug**
- **Harry:** root cause = markup extracted each calc + inclusive tax from markup → re-added markup lacked tax; fixed for new res
- **Ching (payout tomorrow):**
  1. Airbnb markup tax still breaking balances; Advanced deposit off; cash not recognised
  2. VRBO commissions don’t match OTA (only 4 of May checkouts reconcile); JE locked

### 25 Jun — Still finding errors after EOM

Alvan: *“I’m not a fan of Hometime having to check the accuracy of the data in the platform”* — then:

| Account | Res | Failure |
|---------|-----|---------|
| MRP | `HA-bUqRcno7HCn` (VRBO) | CF $555 → owner $504.55; **$50.45 GST stripped, not re-added** |
| MRP | `BC-5A5528F9C` (BDC) | **GST + VAT both applied** on same CF |
| TBC | `HMJBNBWJX8` (Airbnb) | Advanced deposit won’t clear; **GST rounding 15.46 vs 15.45** |

---

## Why confidence collapsed

1. **Declare fixed → client finds more** — repeatedly  
2. **Client does detection** — Alvan/Ching running the real QA  
3. **Multiple bug classes same month** — missing tax → Whitesands FT → wrong GST/markup → cash/AD → VRBO commission  
4. **EOM is the forcing function** — every escalation tied to statements / portal / payout  
5. **Recovery lags code** — “fixed all but two” while Ching still blocked on payout day  

---

## Key client quotes

> “You confirmed yesterday that this issue had been resolved for future reservations. It doesn’t seem to be accurate.” — Alvan, 28 May

> “This contradicts your statement that the new query returned no reservations requiring correction.” — Alvan, 2 Jun

> “I expect Guesty to have tools and reporting to surface tax discrepancies by now… This is quite disappointing.” — Alvan, 4 Jun

> “I’m not a fan of Hometime having to check the accuracy of the data in the platform.” — Alvan, 25 Jun

> “Immediate issues that needs to be resolved ahead of our payout tomorrow.” — Ching, 10 Jun
