# Room Migration Progress (weekly)

Editable weekly slide built by crossing **new accounts created after July 13** with the **Reservations Room Accounts Overview** export.

## Logic

1. Load `data/accounts_created_after_2026-07-13.csv` (`accountId`, `createdAt`)
2. Load `data/room_migration_accounts.csv` (Package, Segment, etc.)
3. Keep only rows whose Account ID appears in both files
4. Break down by **Package** (Lite / Pro / Enterprise) for the progress chart
5. Break down by **Segment** (from the room CSV) in a second slide / CSV

## Deliverables

| File | Purpose |
|------|---------|
| `Room_Migration_Progress.pptx` | Slide 1: progress chart · Slide 2: segment breakdown |
| `exports/room-migration-progress.html` | Browser preview |
| `exports/room-migration-progress.png` | Full-slide PNG snapshot |
| `exports/room-accounts-created-after-july-13.csv` | Consolidated matched accounts |
| `exports/room-accounts-segment-breakdown.csv` | Segment × plan summary |
| `create_room_migration_dashboard.py` | Regenerator |

## Current numbers (from attached exports)

- Created after July 13: **2,876**
- Room accounts overview: **527**
- Matched: **161** (Lite 156 · Pro 5 · Enterprise 0)
- Segment: **SMB 161**

## Weekly update

1. Replace `data/accounts_created_after_2026-07-13.csv` with the latest created-accounts export
2. Replace `data/room_migration_accounts.csv` with the latest Room Accounts Overview export
3. Optional: set `report_week_label` in `room_migration_config.json`
4. Run:

```bash
pip install -r requirements-room-migration.txt
python3 create_room_migration_dashboard.py
```

5. Open `Room_Migration_Progress.pptx` (or upload to Google Drive → Open with Google Slides)

## Open in Google Slides

1. Download `Room_Migration_Progress.pptx`
2. Upload to [Google Drive](https://drive.google.com)
3. Right-click → **Open with → Google Slides**
4. **File → Save as Google Slides**
