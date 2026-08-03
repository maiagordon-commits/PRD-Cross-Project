# Room Migration Progress

Chart of accounts created after July 13 (cumulative, refreshed weekly):

| Box | Formula |
|-----|---------|
| **Total Accounts Created** | all rows in merged created-accounts CSV |
| **Pro** | Account IDs also in Room Accounts Overview |
| **Lite** | Total − Pro |

## Weekly refresh

1. Save the new “accounts created after …” export under `data/` (or merge into `data/accounts_created_after_2026-07-13.csv`)
2. Replace `data/room_migration_accounts.csv` with the latest Room Accounts Overview
3. Run `python3 create_room_migration_dashboard.py`

## Outputs

- `Room_Migration_Progress.pptx` — full weeks including the current partial week
- `Room_Migration_Progress_Clean.pptx` — drops the incomplete current week; no white chart panel; no Cumulative Trends / Week starting labels
- `exports/room-migration-progress.html` / `.png` (+ `-clean` variants)
- `exports/segment-breakdown.csv`
