---
name: quarterly-capex-effort
description: "Calculate end-of-quarter CapEx / capitalization effort in man-months (MM) for strategic programs (AI, Geo, Upsells, ANZ, etc.). Use when the user asks for Q1/Q2/Q3/Q4 effort, CapEx MM, Column D/E paste strings, program man-months, or EoQ AI/Geo effort breakdown from EE weeks and role % sheets."
---

# Quarterly CapEx Effort (MM)

Convert program effort inputs into CapEx spreadsheet paste strings: **Column D** (total MM) and **Column E** (role breakdown).

**MM = man-months**, not Monday Meeting.

## When to use

- End of quarter CapEx / capitalization effort for AI, Geo, or similar programs
- User attaches initiative EE-weeks CSV/Sheet tabs + staffing (% per week)
- User asks to recreate prior-quarter Column D / Column E format

## Inputs to collect

Ask for anything missing before finalizing numbers:

| Input | Required | Notes |
|-------|----------|-------|
| Quarter label | Yes | e.g. `Q3'26` |
| Program name(s) | Yes | AI, Geo, Upsells, … — one output set per program |
| Dev person-weeks | Yes | Sum of initiative EE (weeks); blank EE = 0 |
| Dev headcount IL / UKR | Yes for CapEx split | CSV may say `uk` — eng locations in CapEx are **IL** / **UKR** unless user says otherwise |
| Data team | If present | Prefer **person-weeks**; if only %, use % path (see formulas) |
| Dev TL | If present | Headcount × % per location |
| R&D Director | If present | % per location |
| Product Team Lead / Product Director / VP / PM | If present | Headcount × %; note duration if not full quarter |
| Design | If present | % by location; fold Design TL into Designer unless user wants a separate label |

**Multi-tab sheets:** CSV export is one tab only. If the user says Geo is on tab 2, ask for that tab as a separate CSV/xlsx.

## Constants (2025 template — default)

- Working weeks per quarter: **11** (vacations/holidays removed)
- Months per quarter: **3**
- Round paste values to **1 decimal**

Override only if the user explicitly changes the template.

## Formulas

### Dev (person-weeks)

```
avg_capacity (before × 3) = total_person_weeks ÷ 11
IL_Dev_before = avg_capacity × (IL_devs ÷ total_devs)
UKR_Dev_before = avg_capacity × (UKR_devs ÷ total_devs)
IL_Dev_MM = IL_Dev_before × 3
UKR_Dev_MM = UKR_Dev_before × 3
```

If IL/UKR headcount is missing, emit a single `Dev` segment and note the gap; offer an optional split only if the user supplies or confirms one.

### Data team

- **From weeks:** same as Dev → before = `weeks ÷ 11`, MM = `weeks ÷ 11 × 3`. Label: `Data team`.
- **From % only:** before = `headcount × %`, MM = before × 3. Prefer weeks when both exist.

### %-of-week roles (full quarter)

Applies to: Product Team Lead, Product Director, VP Product, PM, Designer, R&D Director (and Data when %-only).

```
before × 3 = sum of weekly % (or headcount × %)
MM = before × 3
```

### Dev TL (exception)

```
before × 3 = sum of weekly %
MM = before   # do NOT × 3
```

Product Team Lead is **not** a Dev TL — Product TL **does** get × 3.

### Partial-quarter % roles

If user says e.g. “PM for 1 month only”: treat stated value as already MM when they use `headcount × % × months`, and do not × 3 again. Confirm with user when ambiguous.

### Aggregation

- Sum same role + same location into one Column E segment.
- Product Directors across locations: sum into `Product Director` (no location) unless user wants them split.
- Design TLs: fold into `Designer {location}` unless user asks for a Design TL label.
- PM mixed locations: may use single `PM` or split `PM IL`, `PM US`, etc. Prefer split when material; match prior-quarter style if user is updating an existing row.

## Output format (required)

For each program, produce:

### 1. Breakdown table

| Role | Before × 3 | After × 3 (MM) | Notes |
|------|------------|----------------|-------|

### 2. Column D (paste)

```
{total_MM}MM for {Qn}'{YY}
```

Example: `49.1MM for Q3'26`

### 3. Column E — before × 3 (preferred paste)

Comma-separated segments, typical order:

```
{IL Dev}, {UKR Dev}[, {Data team}][, {IL TL}, {UKR TL}][, {R&D Director IL}, {R&D Director UKR}][, {Product Team Lead}][, {Product Director}][, {VP Product IL}][, {PM…}][, {Designer…}]
```

Example:

```
1.8 IL Dev, 3.7 UKR Dev, 2.6 Data team, 1.5 IL TL, 0.9 Product Team Lead, 0.6 Product Director, 0.3 VP Product IL, 3.3 PM, 2.2 Designer IL, 0.5 Designer Spain
```

### 4. Column E — MM (optional second paste)

Same labels, MM values.

### 5. Category rollup

Dev / Data / TL / R&D Director / Product / Design → Total MM.

## Workflow

1. Confirm quarter label and program list.
2. Read attached sheet(s); if multi-program workbook arrived as one CSV, process only what’s present and ask for missing tabs.
3. Sum EE weeks; parse staffing table (Name, Role, Location, Effort %).
4. Apply formulas; show assumptions (11 weeks, UK→UKR, Design TL fold-in, Data % vs weeks).
5. Emit Column D + Column E (before × 3 first).
6. On user corrections (headcount, %, weeks), recalc only affected segments and restate both pastes + new total.

## Do not

- Create a new Google Sheet unless asked — paste strings go into the existing CapEx sheet.
- Use 13 weeks or `weeks ÷ 4` unless the user overrides the 2025 template.
- Apply × 3 to Dev TL MM.
- Blend AI and Geo into one row — one program per Column D/E set.
- Invent IL/UKR splits, TL %, or R&D % when absent; call out gaps.

## Reference

Worked Q2/Q3 examples and label conventions: [references/examples.md](references/examples.md)

Q3’26 full one-pager (original inputs → Column E/D for AI, Geo, Upsells, ANZ): [references/q3-26-capex-one-pager.md](references/q3-26-capex-one-pager.md) · printable [q3-26-capex-one-pager.html](references/q3-26-capex-one-pager.html)
