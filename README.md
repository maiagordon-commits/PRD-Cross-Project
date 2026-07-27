# Guesty status slides & dashboards

Professional Guesty WIP slides and weekly dashboards for Google Slides / PowerPoint.

## Deliverables

| File | Purpose |
|------|---------|
| `E-Invoicing_Challenges_Next_Steps.pptx` | Editable E-Invoicing deck |
| `City_Tax_Challenges_Next_Steps.pptx` | Editable City Tax deck |
| `Room_Migration_Progress.pptx` | Weekly Room Migration Progress slide |
| `create_einvoicing_slide.py` / `create_city_tax_slide.py` | Slide regenerators |
| `create_room_migration_dashboard.py` | Room migration regenerator (from CSV) |
| `GOOGLE_SLIDES_IMPORT.md` / `CITY_TAX_GOOGLE_SLIDES_IMPORT.md` | Import instructions |
| `ROOM_MIGRATION_README.md` | Weekly Room Migration update guide |

## Open in Google Slides

1. Download the `.pptx`
2. Upload to [Google Drive](https://drive.google.com)
3. Right-click → **Open with → Google Slides**
4. **File → Save as Google Slides** for a native shareable link

For Room Migration, replace both CSVs under `data/` each week (created-accounts + room overview), then re-run `python3 create_room_migration_dashboard.py` — see `ROOM_MIGRATION_README.md`.
