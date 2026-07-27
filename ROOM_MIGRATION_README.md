# Room Migration Progress — accounts + Segment

## What this does

1. Takes every account from **accounts created after July 13**
2. Looks up **Segment** in the Reservations Room Accounts Overview by Account ID
3. Writes a consolidated CSV with a **Segment column on every row**
4. Builds the progress chart from that Segment breakdown

## Outputs

| File | Purpose |
|------|---------|
| `exports/accounts_created_with_segment.csv` | All created accounts + **Segment** column |
| `exports/segment-breakdown.csv` | Segment counts |
| `Room_Migration_Progress.pptx` | Chart slide |
| `exports/room-migration-progress.html` / `.png` | Preview |

## Segment column rules

| Situation | Segment value |
|-----------|----------------|
| Account ID found in Room Overview | Value from Room CSV (`SMB`, `Mid-Market`, `SME`, …) |
| Account ID **not** in Room Overview | `Unknown` |

With the current Room Overview export, only ~161 of ~2,876 created accounts have a known Segment. A fuller Room export will fill more rows.

## Weekly update

```bash
# replace these two files, then:
python3 create_room_migration_dashboard.py
```

- `data/accounts_created_after_2026-07-13.csv`
- `data/room_migration_accounts.csv`
