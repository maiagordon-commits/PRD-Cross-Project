# Room Migration Progress — Segment from Guesty

## Goal

1. Start from **only** `data/accounts_created_after_2026-07-13.csv` (~2,876 accounts)
2. Look up each account’s **Segment in Guesty**
3. Write a CSV with a **Segment column per Account ID**
4. Build the progress chart from that Segment breakdown

## Blocker in this cloud environment

Guesty HQ exposes account data at:

```text
GET https://hq.guesty.com/api/accounts/{accountId}
```

Calls from this agent return **`{"message":"Not Authorized"}`**.  
There is no Guesty HQ token/cookie configured here, so Segment cannot be read live from Guesty yet.

The old Room Accounts Overview CSV is **not** a full Guesty segment source (only ~527 rows → 161 overlaps). That is why the breakdown looked wrong.

## How to unblock (pick one)

### Option A — Guesty export (fastest)

From Guesty HQ / Sisense, export **Account ID + Segment** for accounts created after July 13, and save as:

```text
data/guesty_account_segments.csv
```

Columns required:

| Account ID | Segment |
|---|---|
| 6a54a93c… | SMB |

Then run:

```bash
python3 enrich_segments_from_guesty.py
python3 create_room_migration_dashboard.py
```

### Option B — Guesty HQ API auth

Add one secret to the Cloud Agent environment:

- `GUESTY_HQ_TOKEN` — Bearer token, **or**
- `GUESTY_HQ_COOKIE` — browser session cookie from an authenticated HQ session

Then run the same two commands. Lookups are cached in `data/segment_lookup_cache.json`.

## Outputs after enrichment

| File | Purpose |
|------|---------|
| `exports/accounts_created_with_segment.csv` | Every created account + Segment |
| `exports/segment-breakdown.csv` | Counts by Segment |
| `Room_Migration_Progress.pptx` | Chart slide |
| `exports/room-migration-progress.html` / `.png` | Preview |
