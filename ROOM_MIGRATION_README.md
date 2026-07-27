# Room Migration Progress (weekly)

Editable weekly slide for accounts **created after July 13**, enriched with Package / Segment from the Reservations Room Accounts Overview when the Account ID matches.

## Why totals were 161 before

| File | Rows |
|------|------|
| Accounts created after July 13 | **~2,876** |
| Room Accounts Overview | **527** |
| IDs in **both** | **161** |

The first version used an **inner join**, so it dropped the ~2,715 created accounts that are not in the Room Overview export. That export only has Package/Segment for accounts already in it — most brand-new accounts are not there yet.

## Current logic (left join)

1. Start from **all** created accounts (`accountId`, `createdAt`)
2. Left-join Room Accounts Overview by Account ID
3. If matched → use Package (Lite / Pro / Enterprise) and Segment
4. If not matched → count as **Not in Room Overview**

So:

- **Total Accounts Created** = full created-accounts file (~2,876)
- Lite / Pro / Enterprise = only the IDs found in the Room Overview
- Remaining IDs = Not in Room Overview (no Package/Segment available yet)

## Deliverables

| File | Purpose |
|------|---------|
| `Room_Migration_Progress.pptx` | Slide 1: progress chart · Slide 2: segment breakdown |
| `exports/room-migration-progress.html` | Browser preview |
| `exports/room-migration-progress.png` | Snapshot |
| `exports/room-accounts-created-after-july-13.csv` | All created accounts + room fields when matched |
| `exports/room-accounts-segment-breakdown.csv` | Segment × plan summary |

## Weekly update

1. Replace `data/accounts_created_after_2026-07-13.csv`
2. Replace `data/room_migration_accounts.csv` (ideally a fuller Room Overview if you want more Package/Segment coverage)
3. Run `python3 create_room_migration_dashboard.py`

Optional: set `"join_mode": "inner"` in `room_migration_config.json` to restrict again to matched IDs only.
