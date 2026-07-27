# Room Migration Progress (weekly)

Editable weekly slide matching the Room Migration Progress dashboard.

## Deliverables

| File | Purpose |
|------|---------|
| `Room_Migration_Progress.pptx` | PowerPoint / Google Slides import |
| `exports/room-migration-progress.html` | Browser preview (live Chart.js) |
| `exports/room-migration-progress.png` | Full-slide PNG snapshot |
| `create_room_migration_dashboard.py` | Regenerator |
| `data/room_migration_accounts.csv` | Source export (replace weekly) |
| `room_migration_config.json` | Title, chart start, optional week label |

## Weekly update

1. Export the latest **Reservations Room Accounts Overview** CSV.
2. Replace `data/room_migration_accounts.csv` with that file.
3. Optional: set `report_week_label` in `room_migration_config.json` (e.g. `"July 20 - July 24"`). Leave `null` to auto-label from the latest migration week.
4. Run:

```bash
pip install python-pptx matplotlib
python3 create_room_migration_dashboard.py
```

5. Open `Room_Migration_Progress.pptx` (or upload to Google Drive → Open with Google Slides).

## How metrics are calculated

Rows where **Room Migrated?** is true and **Migration Completed At** is a valid date:

- **Total / Lite / Pro / Enterprise** — counts by `Package`
- **Pro Mid Market** — Pro rows whose `Segment` is Mid-Market
- **Cumulative Trends by Plan** — stacked weekly cumulative counts by Monday week-start of `Migration Completed At`, from `chart_start` (default `2026-04-13`) through the latest migration week

## Open in Google Slides

1. Download `Room_Migration_Progress.pptx`
2. Upload to [Google Drive](https://drive.google.com)
3. Right-click → **Open with → Google Slides**
4. **File → Save as Google Slides**
