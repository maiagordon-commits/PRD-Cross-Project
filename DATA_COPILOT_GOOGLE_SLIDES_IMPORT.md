# Data Co-Pilot — Usage Summary (One Slide)

One-slide executive summary of the shared **Data Copilot Usage Report 2026-07-15** canvas.

## Files

| File | Purpose |
|------|---------|
| `Data_Copilot_Usage_Summary.pptx` | Editable one-slide deck |
| `create_data_copilot_slide.py` | Regenerator |
| `exports/data-copilot-usage-summary.html` | Browser preview |
| `DATA_COPILOT_GOOGLE_SLIDES_IMPORT.md` | Import instructions |

## Open as Google Slides

1. Download `Data_Copilot_Usage_Summary.pptx`
2. Upload to [Google Drive](https://drive.google.com)
3. Right-click → **Open with → Google Slides**
4. Optional: **File → Save as Google Slides** for a native shareable link

### Import into an existing deck

1. Open a Google Slides presentation
2. **File → Import slides**
3. Upload the `.pptx`
4. Select the slide → **Import**

## What’s on the slide

- **4 KPIs:** Q2 Total Queries (21,410), Unique Users (3,876), Peak WAU (885), Unique Accounts (3,220)
- **Weekly Active Users** line chart (weeks 1–13) showing pre-GA baseline → GA launch spike → post-GA plateau → week-13 dip
- **Phase cards:** Pre-GA, GA Launch (highlighted), Post-GA

## Regenerate

```bash
python3 create_data_copilot_slide.py
```
