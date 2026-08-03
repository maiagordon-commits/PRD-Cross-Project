#!/usr/bin/env python3
"""
Enrich accounts-created-after-July-13 with Segment from Guesty.

Sources (first match wins):
  1. Guesty HQ API  — if GUESTY_HQ_TOKEN or GUESTY_HQ_COOKIE is set
       GET https://hq.guesty.com/api/accounts/{accountId}
  2. Guesty segment export CSV — data/guesty_account_segments.csv
       Required columns: Account ID (or accountId), Segment

Writes:
  exports/accounts_created_with_segment.csv   (every created account + Segment)
  data/segment_lookup_cache.json              (cached Guesty lookups)
"""

from __future__ import annotations

import csv
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CREATED_CSV = ROOT / "data" / "accounts_created_after_2026-07-13.csv"
SEGMENT_EXPORT = ROOT / "data" / "guesty_account_segments.csv"
CACHE_PATH = ROOT / "data" / "segment_lookup_cache.json"
OUT_CSV = ROOT / "exports" / "accounts_created_with_segment.csv"
HQ_ACCOUNT_URL = "https://hq.guesty.com/api/accounts/{account_id}"

SEGMENT_ALIASES = {
    "smb": "SMB",
    "mid-market": "Mid-Market",
    "mid market": "Mid-Market",
    "midmarket": "Mid-Market",
    "sme": "SME",
    "enterprise": "Enterprise",
}


def normalize_segment(raw: str | None) -> str:
    if raw is None:
        return "Unknown"
    value = str(raw).strip()
    if not value or value.lower() in {"null", "none", "nan", ""}:
        return "Unknown"
    return SEGMENT_ALIASES.get(value.lower(), value)


def load_created() -> list[dict]:
    with open(CREATED_CSV, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_segment_export() -> dict[str, str]:
    if not SEGMENT_EXPORT.exists():
        return {}
    out: dict[str, str] = {}
    with open(SEGMENT_EXPORT, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            account_id = (row.get("Account ID") or row.get("accountId") or row.get("account_id") or "").strip()
            segment = row.get("Segment") or row.get("segment") or row.get("account_segment")
            if account_id:
                out[account_id] = normalize_segment(segment)
    return out


def load_cache() -> dict[str, str]:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def hq_headers() -> dict[str, str] | None:
    token = os.environ.get("GUESTY_HQ_TOKEN", "").strip()
    cookie = os.environ.get("GUESTY_HQ_COOKIE", "").strip()
    headers = {"Accept": "application/json", "User-Agent": "room-migration-dashboard/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        return headers
    if cookie:
        headers["Cookie"] = cookie
        return headers
    return None


def extract_segment_from_payload(payload: dict) -> str:
    """Best-effort Segment extraction from Guesty HQ account payloads."""
    candidates = [
        payload.get("segment"),
        payload.get("Segment"),
        payload.get("accountSegment"),
        payload.get("account_segment"),
        (payload.get("account") or {}).get("segment") if isinstance(payload.get("account"), dict) else None,
        (payload.get("data") or {}).get("segment") if isinstance(payload.get("data"), dict) else None,
        (payload.get("company") or {}).get("segment") if isinstance(payload.get("company"), dict) else None,
    ]
    for value in candidates:
        if value:
            return normalize_segment(str(value))
    # nested custom / crm fields
    for key in ("crm", "hubspot", "metadata", "fields"):
        block = payload.get(key)
        if isinstance(block, dict):
            for k in ("segment", "Segment", "account_segment"):
                if block.get(k):
                    return normalize_segment(str(block[k]))
    return "Unknown"


def fetch_segment_from_hq(account_id: str, headers: dict[str, str]) -> tuple[str, str]:
    url = HQ_ACCOUNT_URL.format(account_id=account_id)
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            payload = json.loads(body) if body else {}
            return extract_segment_from_payload(payload), "hq_api"
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise SystemExit(
                "Guesty HQ API returned Not Authorized. "
                "Set a valid GUESTY_HQ_TOKEN or GUESTY_HQ_COOKIE secret, "
                f"or place a Guesty export at {SEGMENT_EXPORT}."
            ) from e
        if e.code == 404:
            return "Unknown", "hq_api_not_found"
        return "Unknown", f"hq_api_http_{e.code}"
    except Exception as e:  # noqa: BLE001
        return "Unknown", f"hq_api_error:{type(e).__name__}"


def enrich() -> list[dict]:
    created = load_created()
    export_map = load_segment_export()
    cache = load_cache()
    headers = hq_headers()

    print(f"Created accounts: {len(created)}")
    print(f"Guesty segment export rows: {len(export_map)} ({SEGMENT_EXPORT.name if SEGMENT_EXPORT.exists() else 'missing'})")
    print(f"Cached HQ lookups: {len(cache)}")
    print(f"HQ API auth configured: {'yes' if headers else 'no'}")

    if not export_map and not headers and not cache:
        raise SystemExit(
            "Cannot look up Segment in Guesty from this environment without auth.\n\n"
            "Do ONE of the following, then re-run:\n"
            f"  A) Export Account ID + Segment from Guesty HQ / Sisense and save as:\n"
            f"       {SEGMENT_EXPORT}\n"
            "  B) Add environment secret GUESTY_HQ_TOKEN (Bearer) or GUESTY_HQ_COOKIE\n"
            "     so we can call https://hq.guesty.com/api/accounts/{id}\n"
        )

    rows = []
    hq_calls = 0
    for row in created:
        account_id = (row.get("accountId") or "").strip()
        created_at = row.get("createdAt") or ""
        source = "unknown"
        segment = "Unknown"

        if account_id in export_map:
            segment = export_map[account_id]
            source = "guesty_export"
        elif account_id in cache:
            segment = normalize_segment(cache[account_id])
            source = "cache"
        elif headers:
            segment, source = fetch_segment_from_hq(account_id, headers)
            cache[account_id] = segment
            hq_calls += 1
            if hq_calls % 50 == 0:
                save_cache(cache)
                print(f"  HQ lookups so far: {hq_calls}")
            time.sleep(0.05)  # light rate limit

        rows.append(
            {
                "Account ID": account_id,
                "Created At": created_at,
                "Segment": segment,
                "Segment Source": source,
            }
        )

    if hq_calls:
        save_cache(cache)
        print(f"HQ API calls this run: {hq_calls}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Account ID", "Created At", "Segment", "Segment Source"])
        writer.writeheader()
        writer.writerows(rows)

    # summary
    from collections import Counter

    counts = Counter(r["Segment"] for r in rows)
    sources = Counter(r["Segment Source"] for r in rows)
    print(f"Wrote {OUT_CSV} ({len(rows)} rows)")
    print("Segment counts:", dict(counts))
    print("Sources:", dict(sources))
    known = sum(v for k, v in counts.items() if k != "Unknown")
    print(f"Known segment: {known} / {len(rows)}")
    return rows


if __name__ == "__main__":
    enrich()
