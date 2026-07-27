# Room Migration Progress

Chart of accounts created after July 13:

| Box | Formula | Current |
|-----|---------|--------:|
| **Total Accounts Created** | all rows in created-accounts CSV | 2,876 |
| **SMB** | Account IDs also in Room Accounts Overview | 161 |
| **Lite** | Total − SMB | 2,715 |

## Weekly refresh

1. Replace `data/accounts_created_after_2026-07-13.csv`
2. Replace `data/room_migration_accounts.csv` (used only to identify SMB IDs)
3. Run `python3 create_room_migration_dashboard.py`

## Outputs

- `Room_Migration_Progress.pptx`
- `exports/room-migration-progress.html` / `.png`
- `exports/segment-breakdown.csv`
