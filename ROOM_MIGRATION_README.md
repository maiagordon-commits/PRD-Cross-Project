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

### Option B — Guesty HQ API auth (preferred)

Add **one** secret to this Cloud Agent environment:

[Environment settings](https://cursor.com/dashboard/cloud-agents/environments/e/906dc84c-9fbf-41fd-8858-c3a52d470de8)

| Secret name | Value |
|-------------|--------|
| `GUESTY_HQ_COOKIE` | Full `Cookie` header from an authenticated [hq.guesty.com](https://hq.guesty.com) browser session |
| **or** `GUESTY_HQ_TOKEN` | Bearer token if you have one |

**How to copy the cookie (Chrome/Edge):**
1. Log into [https://hq.guesty.com](https://hq.guesty.com)
2. Open DevTools → **Network**
3. Click any `hq.guesty.com/api/...` request
4. Under Request Headers, copy the full **`cookie:`** value
5. Paste it as secret `GUESTY_HQ_COOKIE` (no `Cookie:` prefix needed — just the value)
6. Save the environment, then tell the agent to continue (or re-run)

Then:

```bash
python3 enrich_segments_from_guesty.py
python3 create_room_migration_dashboard.py
```

Lookups are cached in `data/segment_lookup_cache.json` so re-runs are faster.

## Outputs after enrichment

| File | Purpose |
|------|---------|
| `exports/accounts_created_with_segment.csv` | Every created account + Segment |
| `exports/segment-breakdown.csv` | Counts by Segment |
| `Room_Migration_Progress.pptx` | Chart slide |
| `exports/room-migration-progress.html` / `.png` | Preview |
