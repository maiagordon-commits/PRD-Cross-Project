# OTA Financial Data Mapping & Reverse Engineering Playbook

**Audience:** Product, PMO, CFT, Biz Ops, Accounting, Financials  
**Status:** Working draft — synthesized from Internal Workshops #1 & #2 (May 2026) and related internal materials  
**Last updated:** June 14, 2026  
**Maintainers:** Maia Gordon (PMO), Alex Borack (Biz/CFT), Javier Ibarz (Distribution), Rinat Elimelech (Financials)

---

## How to use this document

This playbook merges two internal workshops on **OTA reverse engineering of financial data** into one implementation guide for the product organization.

| Workshop | Date | Focus |
|---|---|---|
| **Workshop #1** | May 20, 2026 | Use-case discovery: where channel data and Guesty configuration diverge during onboarding and reservation import |
| **Workshop #2** | May 28, 2026 | Deep dive on distribution sync, bundled fees, tax setup gaps, and operational decisions for GA rollout |

Use this guide when:
- Onboarding an ENT account with OTA-connected inventory
- Investigating folio discrepancies on imported or live channel reservations
- Designing product behavior around fee/tax/commission mapping
- Communicating expected variances vs. bugs to customers

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Background: why reverse engineering exists](#2-background-why-reverse-engineering-exists)
3. [Core concepts & terminology](#3-core-concepts--terminology)
4. [End-to-end data flow](#4-end-to-end-data-flow)
5. [Channel reference guide](#5-channel-reference-guide)
6. [Forward mapping — Guesty to OTA (implementation)](#6-forward-mapping--guesty-to-ota-implementation)
7. [Reverse mapping — OTA to Guesty (implementation)](#7-reverse-mapping--ota-to-guesty-implementation)
8. [Workshop use cases & patterns](#8-workshop-use-cases--patterns)
9. [Implementation playbook by lifecycle stage](#9-implementation-playbook-by-lifecycle-stage)
10. [Decision log](#10-decision-log)
11. [Known limitations & “working as designed” scenarios](#11-known-limitations--working-as-designed-scenarios)
12. [Tools, checklists & resources](#12-tools-checklists--resources)
13. [Ownership & escalation matrix](#13-ownership--escalation-matrix)
14. [Open items & future work](#14-open-items--future-work)

---

## 1. Executive summary

### The problem

OTAs and Guesty do not share the same financial model. OTAs often:
- Support **fewer fee types** than Guesty
- **Bundle** multiple fees into one guest-facing line (especially Airbnb)
- Apply their own **deduction, rounding, and tax logic** before sending totals to Guesty

Guesty must therefore **reverse engineer** incoming channel totals into the itemized folio the customer configured — while keeping **totals aligned with the OTA (source of truth)**.

When setup on the OTA side differs from Guesty setup — or when historical reservations are imported — discrepancies appear. Many are **configuration or model differences**, not calculation bugs.

### What changed in May 2026

**Automatic OTA Fees Reverse Mapping** reached GA (May 26, 2026). On newly confirmed reservations, Guesty automatically maps incoming OTA fee types back to the correct internal Guesty fee types configured under **Sync to Channel**.

### What this playbook delivers

- Shared vocabulary across Product, Distribution, Financials, and Accounting
- Channel-specific mapping behavior
- Pre/during/post-implementation checklists
- Documented workshop decisions and open gaps
- Escalation paths when folio data does not reconcile

---

## 2. Background: why reverse engineering exists

### 2.1 The structural mismatch

| Dimension | Typical OTA behavior | Guesty behavior |
|---|---|---|
| Fee granularity | Limited fee categories (e.g., one “Management fee”) | Many configurable additional fees |
| Guest presentation | Bundled / all-inclusive pricing | Separated line items for reporting & tax |
| Tax handling | Channel-specific bundling & rounding | Tax per line item (TPLI), inclusive/exclusive models |
| Source of truth on booking | **OTA** for confirmed channel reservations | Guesty config drives direct & pre-sync pricing |

### 2.2 Two directions of mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                        GUESTY SETUP                             │
│  Additional Fees → Sync to Channel → OTA fee type               │
│                     (FORWARD MAPPING)                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ pricing / fee sync (where supported)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OTA (Airbnb, BDC, Vrbo…)                    │
│  Guest books → OTA calculates bundled total                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │ reservation confirmation payload
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GUESTY RESERVATION FOLIO                        │
│  Reverse engineer totals → internal fee/tax line items          │
│                     (REVERSE MAPPING)                           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 When friction is highest

Workshop #1 identified these as the highest-friction implementation moments:

1. **Historical reservation import** — OTA snapshot reflects old PMS/channel setup, not current Guesty config
2. **Merged fees** — multiple Guesty fees mapped to one OTA fee type must be split back proportionally
3. **Markups on fees (Airbnb)** — Guesty extracts markup/tax from bundled OTA totals; line items may not match configured percentages even when totals are correct
4. **Rates & Availability (R&A) connections** — fees may not be bundled into channel rent at pricing push time, causing negative accommodation fare on deduction
5. **Tax setup timing gaps** — reservations created between FT enablement and tax configuration may miss extraction
6. **Payment recording** — channel payout correct but Guesty payments recorded only against AF + tax, not full fee stack

---

## 3. Core concepts & terminology

| Term | Definition |
|---|---|
| **Forward mapping** | Mapping a Guesty additional fee type to an OTA-supported fee category before/during sync |
| **Reverse mapping** | Mapping an incoming OTA fee type on a confirmed reservation back to the configured Guesty fee type(s) |
| **Fee merge** | Multiple Guesty fee types mapped to the same OTA fee type; values are combined when syncing outbound |
| **Proportional split** | On reverse mapping, merged OTA amounts are distributed across Guesty fee types by configured ratio |
| **Bundled fees** | Fees included in accommodation fare / channel rent on the OTA side |
| **Reverse engineering / de-bundling** | Extracting Guesty line items from OTA-provided totals |
| **Source of truth** | For confirmed OTA reservations, the **OTA payload** is authoritative for amounts received |
| **R&A connection** | Rates & Availability only — fees/taxes may not sync; channel-side fee setup may diverge |
| **Full sync** | Full content + pricing + fees sync model (channel-dependent) |
| **TPLI** | Tax Per Line Item — taxes stored/displayed per invoice line |
| **BEAST tools** | Internal support tools for fee sync inspection, migration, and bulk operations |

### Folio line naming (guest folio)

Each additional fee can show three names:
1. **Guesty fee type** — used in reports, accounting, owner statements
2. **Fee type on channel** — what the guest/OTA displayed
3. **Guesty fee name** — internal freeform label

---

## 4. End-to-end data flow

### 4.1 Happy path (new live reservation)

1. Customer configures additional fees in Guesty
2. Customer maps each fee to supported **Sync to Channel** OTA type (forward mapping)
3. Guesty syncs fee configuration to OTA where supported
4. Guest books on OTA; OTA sends confirmation payload
5. Guesty validates incoming fee types against forward mapping
6. **Reverse mapping (GA)** remaps OTA fees to internal Guesty types automatically
7. Financials distributes taxes/markups; Accounting folio reflects mapped types

### 4.2 Failure paths (workshop-identified)

| Stage | Symptom | Likely cause |
|---|---|---|
| Pricing push | Guesty rent ≠ OTA rent | Fees not bundled on channel (R&A); conditional/LOS fees unsupported on Airbnb |
| Confirmation | Unexpected fee type in folio | Unmapped OTA fee → Guesty auto-maps to closest type (warning shown) |
| Confirmation | Merged fee split looks “wrong” | Proportional split across unequal Guesty fee values |
| Import | Totals OK, line items wrong | Historical OTA setup ≠ current Guesty setup |
| Import | Missing taxes | Tax FT enabled before Guesty tax config completed |
| Post-conf | Balance due / overpaid | Payments recorded against subset of line items |
| Accounting | Fee in guest folio missing in accounting folio | Fee not in additional fees setup or BM/NRI config mismatch |

---

## 5. Channel reference guide

### 5.1 Airbnb

**Connection models:** Full sync nuances; R&A + bundled fees FT is critical for fee-in-rent behavior

| Topic | Behavior | Implementation note |
|---|---|---|
| Outbound fee sync | Airbnb does **not** support date-range or LOS-dependent fees the way Guesty does | PMS may send one value to channel but apply different logic on reservation — validate with reservation ID |
| Bundling | Airbnb bundles & deducts on its side | Guesty reverse-engineers markup/tax from received totals |
| Markups on fees | Supported (FIN) | Perceived “gaps” vs configured % often WAD — totals match Airbnb |
| Commission | Host service fee + tax (`hostServiceFeeTax`) | Requires `FIN_channel_commission_breakdown` FT; watch `isChannelUpdate` on request-to-book |
| Imported reservations | Common pain point | May need tax-inclusive migration + manual review |
| Source of truth | Airbnb totals | Guesty line items are reconstructed |

**Workshop example (May 20):** Reservation `HM32M4CCZS` — Airbnb cleaning fee $108 vs Vacasa import sheet $128. Root cause class: **PMS sent end-result value to channel** or **different logic at reservation time** vs listing sync.

### 5.2 Booking.com

| Topic | Behavior | Implementation note |
|---|---|---|
| Full sync | Receives sum amounts incl. taxes on AF + additional fees (excl. CF in some models) | Guesty calculates: `fareAccommodation = totalAmount - sum(inclusive invoiceItems)` |
| R&A connection | Fees/taxes **not synced** at pricing level | User must manage fees on BDC; Guesty receives amounts on confirmation only |
| Historical tax on property | Taxes on BDC before Guesty connection persist on old reservations | Cannot remove retroactively from BDC — expect import variance by booking date |
| Payments | Payout from BDC may be correct while Guesty shows underpaid | Verify payments recorded against **all** fee lines, not just AF + tax |

### 5.3 Vrbo

| Topic | Behavior | Implementation note |
|---|---|---|
| Payload | XML includes fee/tax breakdown | More granular than BDC |
| Calculation model | Today: Guesty may calculate from config | **Planned:** use OTA as source of truth (similar to Airbnb/BDC) |
| Promotions | New reservation support; imported edge cases need explicit mapping rules | Confirm scope per release |
| Imported lump-sum taxes | May require spreadsheet/API bulk correction | Coordinate with API team |

### 5.4 Direct / manual / imported reservations

| Topic | Behavior | Implementation note |
|---|---|---|
| No OTA payload | Guesty config is source of truth | Reverse mapping not applicable |
| Upload / import | `createdAt` ≠ booking date | Use **Booking Date** column (Reservations Upload Template col R) for PriceLabs/Wheelhouse accuracy |
| Historical import timing | High risk during EOM / owner statement cycles | Defer bulk import; enable required FTs immediately before import |

---

## 6. Forward mapping — Guesty to OTA (implementation)

### 6.1 Configuration steps (customer-facing)

1. **Additional Fees** → create fee types with amounts/conditions
2. **Sync to Channel** → map each fee to OTA-supported type per channel
3. Review **merge warnings** when multiple Guesty types map to one OTA type
4. Enable channel sync toggles per listing
5. Run **BEAST: Syncing additional fees with OTAs** after material config changes
6. Monitor sync warnings for unsupported fee configurations

### 6.2 Product rules

- If Guesty fee types differ in value and share one OTA type, outbound sync **merges values**
- Unsupported Guesty conditions (LOS, date range) may silently fail or push simplified values on Airbnb
- R&A listings may **not** bundle fees into rent unless bundled-fees FT + correct pricing push — validate before go-live

### 6.3 Pre-go-live validation (per listing sample)

- [ ] Compare Guesty calendar rent vs OTA extranet for same dates
- [ ] Confirm each additional fee appears under expected OTA category
- [ ] Test conditional fee listing → verify OTA response (Airbnb: expect limitation)
- [ ] For R&A: confirm whether fees are in rent or separate on channel
- [ ] Document channel HotelId / listing ID relationships (BDC multi-ID cases)

---

## 7. Reverse mapping — OTA to Guesty (implementation)

### 7.1 GA scope (May 2026)

**In scope:**
- Automatic reverse mapping of OTA fee types → configured Guesty fee types on **newly confirmed** reservations
- Accurate visibility in Guest Folio, Accounting Folio, Financial & Accounting Reports
- Splitting merged fees back to multiple Guesty types (proportionally)

**Out of scope / limitations:**
- **Not retroactive** — existing reservations are not migrated
- Unmapped OTA fees still fall back to closest Guesty type with folio warning
- Manual folio adjustment still required for edge cases

### 7.2 Example

Incoming Airbnb **Management Fee** $200 maps to:
- Guesty **Credit Card Processing Fee** only, or
- Split across **two merged Guesty fees** proportionally

### 7.3 Accounting alignment

Accounting users should validate after go-live:
- Business Models include expected fee types in NRI / deductions
- Additional Fee setup matches Sync to Channel mapping
- Owner statements reflect Guesty fee **types**, not OTA display names

**HC references:**
- [How channel additional fees appear in Guesty (Reverse mapping)](https://help.guesty.com/hc/en-gb/articles/23771841142941-How-channel-additional-fees-appear-in-Guesty-Reverse-mapping)
- [Accounting and additional fee reverse mapping](https://help.guesty.com/hc/en-gb/articles/35376796233117-Accounting-and-additional-fee-reverse-mapping)

### 7.4 Manual correction pattern

When auto mapping is wrong on a live reservation:
1. Set incorrect mapped Guesty fee line to **zero**
2. Add/adjust line item with preferred fee mapping
3. Fix forward mapping to prevent recurrence
4. Reprocess only when approved (watch accounting locks / disbursements)

---

## 8. Workshop use cases & patterns

> Template used in Workshop #1: [Synthesizing Data Accuracy for Imported OTA Bookings](https://docs.google.com/spreadsheets/d/1XnLucNJ1H4WhMhVePXKw_j0xVFKVUVE6fq7-oNbp0js/edit?gid=774243903#gid=774243903)

### UC-01 — Imported OTA reservations with outdated channel setup

**Scenario:** Customer imports historical Airbnb/BDC reservations after connecting Guesty. OTA fee/tax structure reflects **previous PMS**, not current Guesty additional fees.

**Symptoms:** Owner statements wrong; rent includes fees customer expects separated; cleaning fee “missing” from business model.

**Decision:** Treat as **implementation/setup mismatch**, not default recalculation bug. Requires import plan: identify reservations, reprocess or manual adjustment, align listing fee config **before** import.

**Owners:** Alex Borack (Biz), Javier Ibarz (Distribution), FIN/ACC for reprocess policy

---

### UC-02 — PMS sends channel end-state, not Guesty-configured fee

**Scenario:** Previous PMS pushed **final computed values** to OTA (e.g., $128 cleaning on sheet) while Airbnb stores **$108** from its own bundle logic.

**Symptoms:** Imported folio ≠ customer spreadsheet; owner paid on spreadsheet assumptions.

**Decision:** Validate **reservation-level payload** vs listing sync. Educate customer that OTA-confirmed amount is authoritative.

**Workshop evidence:** `HM32M4CCZS` — Airbnb $108 vs Vacasa sheet $128.

---

### UC-03 — Airbnb conditional / LOS fees unsupported on channel

**Scenario:** Guesty fees vary by date range or length of stay; Airbnb rejects or ignores conditional sync.

**Symptoms:** OTA response errors; fee amounts on channel don’t match Guesty listing settings.

**Decision:** Do not promise 1:1 conditional fee parity on Airbnb. Options: simplify fee structure for Airbnb listings, absorb variance in markup, or manual folio handling.

**Owners:** Javier Ibarz (Distribution), Rinat Elimelech (FIN)

---

### UC-04 — Markup on fees (Airbnb) — perceived vs actual gap

**Scenario:** Customer configures markup (e.g., 18.34%) but individual folio lines don’t match naive percentage math.

**Symptoms:** CSM tickets alleging calculation bugs; Alloggio-style audits.

**Decision:** **Working as designed** when totals reconcile to Airbnb. Guesty de-bundles bundled OTA totals using internal extraction formula.

**Customer comms template:** Available via FIN-10159 / Alloggio internal thread — explain bundled OTA model vs Guesty separated lines.

**Owners:** Rinat Elimelech (FIN PM), LDS for customer-facing explanation

---

### UC-05 — Merged fees + reverse mapping

**Scenario:** Multiple Guesty fees → one OTA “Resort/Management fee”; reverse mapping must split incoming amount.

**Symptoms:** Individual fee lines look arbitrary but sum is correct; accounting attribution unclear.

**Decision:** Forward mapping must be deliberate. After GA, new reservations auto-split proportionally. Legacy reservations: manual adjustment or bulk reprocess (if approved).

---

### UC-06 — Rates & Availability + bundled fees not in rent

**Scenario:** Listing uses R&A; bundled fees FT enabled but pricing push didn’t add fees to rent → AF lower than total fees → **negative AF** on deduction.

**Symptoms:** Hometime/Avari-class tax extraction failures; folio discrepancies on R&A listings.

**Decision (May 28 workshop):** Move bundled-fees-for-linked-listings FT toward **GA for new customers** after:
1. Legal review (UI previously notified fees aren’t bundled under R&A)
2. Remove misleading tooltip (FIN PM)
3. Enable for all new accounts (Distribution)
4. Execute MTC for existing accounts

**Owners:** Javier Ibarz, Pawel Rytel (FT), Ella Waldman (Legal), Rinat Elimelech (FIN)

---

### UC-07 — Tax setup timing gap

**Scenario:** Account added to Tax Inclusive / TPLI FT before customer completes tax configuration.

**Symptoms:** Imported Airbnb reservations without inclusive tax extraction; exclusive tax behavior on inclusive account.

**Decision:** OB checklist must enforce **tax config complete** before import/connect. Use migration tools for fix-forward.

**Owners:** Alex Fischer Birnbaum (FIN ops), Harry Houldsworth (OB)

---

### UC-08 — BDC payment recorded on partial line items

**Scenario:** BDC payout correct; Guesty payments logged against AF + tax only.

**Symptoms:** Reservations appear underpaid; owner statement revenue wrong.

**Decision:** User/process fix for historical; product to verify auto-payment allocation covers all imported fee lines.

---

### UC-09 — Channel commission tax not deducted from payout

**Scenario:** `hostServiceFeeTax` parsed but not added as invoice item when `isChannelUpdate=false` (request-to-book).

**Symptoms:** Total payout in folio ≠ Airbnb UI.

**Decision:** FIN defect — fix in host service calculation; part of broader `isChannelUpdate` refactor.

---

### UC-10 — Bulk historical import during EOM

**Scenario:** Customer requests large historical import during owner statement week.

**Decision (May 28):** **Defer** import when risk to balances/JEs exceeds capacity. Prefer post-payout window; enable FT immediately pre-import; batch uploads (~1k) via UI with validation (`sum(invoice items) = total paid`).

**Owners:** Maia Gordon (PMO), Ella Waldman, Gil Wasserman, Alex Borack

---

## 9. Implementation playbook by lifecycle stage

### Phase A — Discovery & design (T-8 to T-4 weeks)

| Step | Action | Owner |
|---|---|---|
| A1 | Inventory all additional fees, taxes, markups, commissions | Customer + CFT |
| A2 | Document current OTA fee categories per listing (extranet screenshots) | CFT |
| A3 | Identify merged fee strategies (what can collapse to OTA types) | FIN PM + Customer |
| A4 | Flag unsupported patterns (LOS/date fees on Airbnb, R&A listings) | Distribution |
| A5 | Decide import strategy: live-only vs historical; cutoff dates | PMO + Biz + ACC |
| A6 | Confirm accounting: BM, NRI, TPLI/inclusive model, recognition rules | ACC PM |

### Phase B — Configuration (T-4 to T-1 weeks)

| Step | Action | Owner |
|---|---|---|
| B1 | Build additional fees in Guesty | Customer/CFT |
| B2 | Complete **Sync to Channel** forward mapping per OTA | Customer/CFT |
| B3 | Enable required FTs (see §12.2) | PMO + R&D |
| B4 | Complete tax configuration **before** channel connect/import | Customer + FIN ops |
| B5 | Run BEAST fee sync + listing-level verification sample | LDS/T3 |
| B6 | Validate R&A vs full sync per listing; test rent parity sheet | Distribution |
| B7 | Align channel commission + markup settings | FIN |

### Phase C — Connection & first reservations (Go-live week)

| Step | Action | Owner |
|---|---|---|
| C1 | Connect channels in controlled batches | CFT |
| C2 | Monitor first 24–72h reservations per channel daily | CFT + PMO |
| C3 | Compare folio to OTA extranet for **every** discrepancy | CFT |
| C4 | Classify: setup vs bug vs WAD (§11) | PMO + FIN + Distribution |
| C5 | No bulk historical import during EOM unless exec-approved | PMO + ACC |

### Phase D — Historical import (if applicable)

| Step | Action | Owner |
|---|---|---|
| D1 | Freeze owner statements until import plan approved | Biz + ACC |
| D2 | Enable FTs immediately before import | R&D |
| D3 | Split files ≤1k reservations; validate totals column | CFT |
| D4 | Import via UI; track failures (payment total mismatch = common) | CFT |
| D5 | Post-import: remove erroneous JEs via approved ACC/T3 process | ACC |
| D6 | Update booking dates for revenue tools (col R / API) | CFT + API |

### Phase D — Steady state & regression prevention

| Step | Action | Owner |
|---|---|---|
| E1 | Monthly audit: sample reservations per channel | CFT |
| E2 | After fee mapping changes, verify **new** reservations only (GA limit) | FIN PM |
| E3 | Update HC/customer docs when mapping changes | Product Marketing |
| E4 | Track discrepancies in shared sheet with Owner / Action / Status | PMO |

---

## 10. Decision log

| # | Date | Decision | Rationale | Status |
|---|---|---|---|---|
| D-01 | May 20, 2026 | Workshop use cases documented in shared spreadsheet template | Align Biz + Product on concrete scenarios | ✅ Active |
| D-02 | May 20, 2026 | OTA reservation payload is authoritative for confirmed amounts | Prevents endless “fix to match spreadsheet” loops | ✅ Active |
| D-03 | May 26, 2026 | Reverse mapping GA for **new** reservations only | Avoid retroactive accounting risk | ✅ Shipped |
| D-04 | May 28, 2026 | Bundled fees FT → GA path for **new customers** | Prevent negative AF / tax extraction failures on R&A | 🔄 In progress |
| D-05 | May 28, 2026 | Legal review required before GA (UI previously disclosed R&A limitation) | Reduce customer trust risk | 🔄 Pending |
| D-06 | May 28, 2026 | Defer Avari-scale historical import during EOM | Protect owner statements & dev capacity | ✅ Decided (case-by-case override requires exec alignment) |
| D-07 | May 28, 2026 | Hometime discrepancy tracker: zero new unexplained discrepancies | Operational quality bar | ✅ Active |
| D-08 | Jun 2026 | Vrbo to move toward OTA-as-source-of-truth for fees/taxes | Align with Airbnb/BDC model | 📋 Planned |

---

## 11. Known limitations & “working as designed” scenarios

Use this section before opening FIN/Distribution defects.

| Symptom | Likely classification | Response |
|---|---|---|
| Markup % on line ≠ configured % but totals match Airbnb | **WAD** — de-bundling math | Use customer comms template; cite FIN-10159 pattern |
| BDC R&A reservation fees unlike Guesty listing | **WAD** — fees not synced on R&A | Manage on BDC; Guesty uses confirmation payload |
| Old BDC reservations include taxes after property tax removal | **WAD** — historical channel state | Explain booking-date cutoff |
| Merged fee split proportions look odd | **WAD** — proportional reverse split | Validate sum; adjust forward mapping if business-wrong |
| Reverse mapping not applied to old reservations | **Known limitation** — GA scope | Manual adjustment or approved reprocess |
| Guesty rent ≠ OTA on R&A before bundled fees GA | **Known gap** — pricing push | Enable FT / fix listing; track Javier sheet |
| Penny rounding on imported sheets | **Data prep issue** | Fix upload formulas before import |

**Non-negotiables (from ENT onboarding practice):**
- Do not recommend disconnecting live OTA listings to fix MU association without E2E data-loss plan
- Do not duplicate thousands of properties as a workaround for MU limits
- Do not lose fees, taxes, photos, or content during inventory transitions

---

## 12. Tools, checklists & resources

### 12.1 Internal documents & templates

| Resource | Link | Purpose |
|---|---|---|
| Workshop use case template | [Google Sheet](https://docs.google.com/spreadsheets/d/1XnLucNJ1H4WhMhVePXKw_j0xVFKVUVE6fq7-oNbp0js/edit?gid=774243903#gid=774243903) | Capture & prioritize mapping scenarios |
| Synthesizing Data Accuracy for Imported OTA Bookings | Slack file F0B4QQ1LBEZ | Pre-workshop data accuracy framework |
| Playbook: Reverse Engineer Channel Reservations | Slack file F0AUV8KGX5G (Alex Borack) | CFT operational reverse-engineering steps |
| Reverse Mapping MTC Process V2 | Slack file F0ANEK9SX19 | Moving the Cheese for reverse mapping GA |
| TPLI / Airbnb options doc | Slack file F096KA6J9T7 | Tax per line item migration decisions |
| Product education — Reverse mapping | [Google Drive folder](https://drive.google.com/drive/folders/1rcaTzyD0BcPu9TLXo6jWHU2RFHXNa2JN) | Demos & enablement |
| Rollout sheet — Reverse mapping | [Google Sheet](https://docs.google.com/spreadsheets/d/14jvSOOEy6qPx1Cp5d7K4n2PHLIIul7yn9nDv906dS5U/edit) | GA tracking |

### 12.2 BEAST / support tools (IKB)

- BEAST: Syncing additional fees with OTAs
- BEAST: Using the Reservation Financials Inspector
- BEAST: Look up additional fees listing setup per channel
- BEAST: Copying additional fees to multiple listings

### 12.3 FTs commonly required for ENT OTA mapping (US accounts — draft)

> PMO thread May 28, 2026: compile authoritative mandatory FT package per PM. Until published, verify per account:

| FT / capability | Typical need |
|---|---|
| Tax Inclusive / TPLI | Tax extraction accuracy |
| FIN_channel_commission_breakdown | Airbnb commission tax in folio |
| Bundled fees for linked listings | R&A fee-in-rent |
| Reverse mapping | Auto OTA→Guesty fee remap (GA) |
| Markups on fees | Airbnb markup extraction |
| Accounting upon payment | Recognition timing |

### 12.4 Pre-flight checklist (printable)

**Account setup**
- [ ] All additional fees created with final names/types
- [ ] Sync to Channel mapping complete for every OTA in scope
- [ ] Merge strategy documented where Guesty fees > OTA types
- [ ] Taxes configured and verified (not just FT-enabled)
- [ ] Business Models reference correct fee types
- [ ] Channel commission settings validated

**Listing / channel**
- [ ] Connection type documented per listing (Full vs R&A)
- [ ] Sample listing rent parity verified on OTA extranet
- [ ] BEAST fee sync executed post-config
- [ ] Unsupported conditional fees flagged to customer

**Import (if applicable)**
- [ ] Import window avoids EOM / owner payouts
- [ ] FTs enabled immediately before import
- [ ] Files validated: Σ line items = total paid
- [ ] Booking dates populated for revenue integrations
- [ ] JE cleanup plan approved by Accounting

**Post-go-live monitoring (first 14 days)**
- [ ] Daily reservation sample audit per channel
- [ ] Discrepancy log with owner + action + status
- [ ] Zero untracked new discrepancies policy

---

## 13. Ownership & escalation matrix

| Domain | Primary owner | Escalation topics |
|---|---|---|
| **PMO / cross-product** | Maia Gordon | Workshop outcomes, ENT OB package, import timing, exec comms |
| **Biz / CFT** | Alex Borack | Customer setup, import execution, use case validation |
| **Distribution / channels** | Javier Ibarz | BDC/Airbnb/Vrbo sync, R&A bundling, extranet parity |
| **Financials PM** | Rinat Elimelech | Reverse mapping, markups, fees conditions, folio calculation |
| **Accounting PM** | Rotem Meir | BM/NRI, JE impact, owner statements, bulk reversals |
| **FIN dev escalation** | Roi Mehalel / FIN team | Calculation defects, FT behavior, reprocess |
| **ACC dev escalation** | Rotem Meir / ACC team | Accounting folio mismatches, disbursement blockers |
| **LDS / T3** | Mariana Viñas / BEAST | Tooling, bulk fee copy, inspection tickets |

**Escalation rule:** Classify first (§11). If true defect, route to FIN vs Distribution vs ACC based on whether issue originates in **payload**, **calculation**, or **accounting mapping**.

---

## 14. Open items & future work

| Item | Owner | Notes |
|---|---|---|
| Publish consolidated workshop summary from Gemini notes | Maia Gordon | Merge into this doc when source notes uploaded |
| Mandatory ENT FT package (US) | All PMs (`#onlyproduct` thread) | Single OB handout for CFT |
| Bundled fees GA + MTC | Javier / Rinat / Ella | Legal + tooltip removal + new-account enablement |
| Vrbo OTA-as-source-of-truth | Rinat / FIN + Distribution | Cross-functional initiative |
| Reverse mapping retroactive migration policy | FIN + ACC | Currently out of GA scope — customer comms needed |
| Grand Welcome field-mapping matrix per OTA | Distribution PMs | Customer request — set expectations on effort |
| Improve import validator (total paid vs line items) | Yarin / Upload team | Reduce Avari-class upload failures |
| `isChannelUpdate` refactor | FIN dev | Prevents commission tax gaps on request-to-book |

---

## Appendix A — Glossary of common tickets / patterns

| Pattern | Example tickets / refs |
|---|---|
| Markup variance | FIN-10159, Alloggio threads |
| Taxes not mapping to accounting | FIN-10768, ACC-5926 |
| Negative AF / bundled fees | T3-166405, Avari/Hometime sheets |
| BDC payment allocation | FIN-10623, Hometime May 13 deep dive |
| Channel commission tax | FIN channel commission breakdown / calculateHostService |

---

## Appendix B — Related workshop participants

| Name | Role |
|---|---|
| Maia Gordon | PMO — workshop lead |
| Alex Borack | Biz/CFT — use cases & implementation |
| Javier Ibarz | Distribution — channel sync & bundling |
| Ella Waldman | Product leadership |
| Rinat Elimelech | Financials PM |
| Rotem Meir | Accounting PM |
| Vadym Padalko | R&D (approved workshop) |

---

*This document should be treated as a living playbook. When Gemini workshop notes and the finalized use-case spreadsheet are available, merge them into §8 and §10 and remove any interim drafting notes.*
