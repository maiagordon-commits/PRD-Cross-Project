# Quarterly CapEx Effort — Worked Examples

Label conventions and sample pastes from Q2'26 / Q3'26 runs. Use as style reference; always recompute from current inputs.

## Column E role labels

| Role | Label |
|------|--------|
| Engineers IL / UKR | `IL Dev`, `UKR Dev` |
| Combined eng (no split) | `Dev` |
| Data Science / data eng | `Data team` |
| Engineering team leads | `IL TL`, `UKR TL` |
| R&D directors | `R&D Director IL`, `R&D Director UKR` |
| Product TLs | `Product Team Lead` |
| Product directors (often summed) | `Product Director` |
| VP Product | `VP Product IL` |
| Product managers | `PM`, `PM IL`, `PM US`, … |
| Design (incl. Design TL unless split) | `Designer IL`, `Designer Spain` |

## Q2'26 — AI Program (final state)

**Inputs (illustrative):** 75 person-weeks; 10 devs (4 IL / 6 UKR); Data 9 weeks; IL TL 2×80%; UKR TL 3×30%; R&D Dir IL 50% / UKR 10%; Product TL 100%+50%; PD 20%+10%; VP 30%; PM 8×50%×1 month; Design IL 1.4 / Spain 0.2 before.

**Column D:** `42.4MM for Q2'26`

**Column E (before × 3):**
```
2.7 IL Dev, 4.1 UKR Dev, 0.8 Data team, 1.6 IL TL, 0.9 UKR TL, 0.5 R&D Director IL, 0.1 R&D Director UKR, 1.5 Product Team Lead, 0.3 Product Director, 0.3 VP Product IL, 4.0 PM IL, 1.4 Designer IL, 0.2 Designer Spain
```

## Q2'26 — Geo Expansion (final state)

**Inputs (illustrative):** 22.5 person-weeks; 10 devs (2 IL / 8 UKR); IL TL 10%+50%; UKR TL 3×10%; R&D Dir IL 5%+20%; PM 5×30%; PD 2×20%; Design IL combined 20%.

**Column D:** `14.1MM for Q2'26`

**Column E (before × 3):**
```
0.4 IL Dev, 1.6 UKR Dev, 0.6 IL TL, 0.3 UKR TL, 0.25 R&D Director IL, 1.5 PM, 0.4 Product Director, 0.2 Designer IL
```

## Q3'26 — AI Program (after 6 IL / 12 UKR update)

**Inputs:** 60.63 person-weeks; 18 devs (6 IL / 12 UKR); Data 3×85%; IL TL 100%+40%+10%; Product TL 50%+40%; PD 30%+30%; VP 30%; PM 11×30%; Design IL 220%; Design Spain 50%.

**Column D:** `49.1MM for Q3'26`

**Column E (before × 3):**
```
1.8 IL Dev, 3.7 UKR Dev, 2.6 Data team, 1.5 IL TL, 0.9 Product Team Lead, 0.6 Product Director, 0.3 VP Product IL, 3.3 PM, 2.2 Designer IL, 0.5 Designer Spain
```

**Column E (MM):**
```
5.5 IL Dev, 11.0 UKR Dev, 7.7 Data team, 1.5 IL TL, 2.7 Product Team Lead, 1.8 Product Director, 0.9 VP Product IL, 9.9 PM, 6.6 Designer IL, 1.5 Designer Spain
```

## Q3'26 — Geo Program

**Inputs:** 22.5 weeks (Fin Loc 12.5 + Cross 4 + Distribution 6); PD 15%+30%; PM 40%+30%; Design 10%. No IL/UKR headcount in file → unsplit `Dev`.

**Column D:** `9.9MM for Q3'26`

**Column E (before × 3):**
```
2.0 Dev, 0.5 Product Director, 0.7 PM, 0.1 Designer IL
```

## Sanity checks

- `sum(Dev before) ≈ total_person_weeks ÷ 11`
- `sum(all MM) = Column D number`
- Changing only IL/UKR headcount **re-splits** Dev; **total Dev MM and program MM stay the same** if weeks unchanged
- CSV/Sheets: each tab must be exported separately for multi-program workbooks
