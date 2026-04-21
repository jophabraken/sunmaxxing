#!/usr/bin/env python3
"""
ZOEY — Google Search Console fetcher.

Pulls yesterday's impressions, clicks, avg position, and top queries for
sunmaxxing.com. Splits Berlin-country data from the global total.

Usage:
    python3 tools/zoey_gsc.py              # prints yesterday's summary
    python3 tools/zoey_gsc.py --days 7     # last 7 days
    python3 tools/zoey_gsc.py --json       # machine-readable output

Requires:
    .secrets/gsc-key.json    service-account key (NOT committed)
    pip install google-api-python-client google-auth

ZOEY reads this file every morning. Don't break the --json contract without
also updating the playbook.
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parent.parent
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# Look for the key in two places:
#  1. repo-local .secrets/ (gitignored) — useful for dev sessions
#  2. /sessions/nice-inspiring-cerf/mnt/outputs/.secrets/ — persistent across
#     Cowork sessions, on Jop's computer. ZOEY's scheduled task uses this one.
CANDIDATE_KEY_PATHS = [
    ROOT / ".secrets" / "gsc-key.json",
    Path("/sessions/nice-inspiring-cerf/mnt/outputs/.secrets/gsc-key.json"),
    Path(os.environ.get("ZOEY_GSC_KEY", "")),  # escape hatch
]
KEY_PATH = next((p for p in CANDIDATE_KEY_PATHS if p and p.exists()), None)

# Our GSC properties. Try both — domain property first, falls back to URL prefix.
PROPERTIES = [
    "sc-domain:sunmaxxing.com",
    "https://sunmaxxing.com/",
]


def get_service():
    if KEY_PATH is None or not KEY_PATH.exists():
        checked = "\n  ".join(str(p) for p in CANDIDATE_KEY_PATHS if p)
        sys.exit(
            "FATAL: gsc-key.json not found. Checked:\n  "
            f"{checked}\n→ See /docs/zoey-playbook.md for setup."
        )
    creds = service_account.Credentials.from_service_account_file(
        str(KEY_PATH), scopes=SCOPES
    )
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def pick_property(service):
    """Return the first property this service account can query."""
    last_err = None
    for prop in PROPERTIES:
        try:
            # Cheap no-op query — just checking access.
            service.searchanalytics().query(
                siteUrl=prop,
                body={
                    "startDate": (date.today() - timedelta(days=3)).isoformat(),
                    "endDate": (date.today() - timedelta(days=2)).isoformat(),
                    "rowLimit": 1,
                },
            ).execute()
            return prop
        except HttpError as e:
            last_err = e
            continue
    raise RuntimeError(
        f"No accessible GSC property. Last error: {last_err}\n"
        "→ Check that zoey-gsc-reader@sunmaxxing-seo.iam.gserviceaccount.com "
        "is added as a user in Search Console."
    )


def query(service, prop, start, end, dimensions=None, row_limit=1000, filters=None):
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "rowLimit": row_limit,
    }
    if dimensions:
        body["dimensions"] = dimensions
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]
    try:
        return service.searchanalytics().query(siteUrl=prop, body=body).execute()
    except HttpError as e:
        return {"error": str(e), "rows": []}


def summarize(rows):
    if not rows:
        return {"impressions": 0, "clicks": 0, "avg_position": None, "ctr": 0.0}
    total_impressions = sum(r.get("impressions", 0) for r in rows)
    total_clicks = sum(r.get("clicks", 0) for r in rows)
    # weighted avg position
    if total_impressions:
        weighted_pos = (
            sum(r.get("position", 0) * r.get("impressions", 0) for r in rows)
            / total_impressions
        )
    else:
        weighted_pos = None
    ctr = (total_clicks / total_impressions) if total_impressions else 0.0
    return {
        "impressions": total_impressions,
        "clicks": total_clicks,
        "avg_position": round(weighted_pos, 2) if weighted_pos else None,
        "ctr": round(ctr, 4),
    }


def fetch(days=1):
    service = get_service()
    prop = pick_property(service)
    end = date.today() - timedelta(days=1)  # GSC is 1-day lagged
    start = end - timedelta(days=days - 1)

    # 1. Global totals
    global_rows = query(service, prop, start, end).get("rows", [])
    global_summary = summarize(global_rows)

    # 2. Berlin-country split (country = DEU) — proxy for "Berlin audience"
    #    until we can filter by city (not available in the Search Analytics API).
    de_filter = [{"dimension": "country", "operator": "equals", "expression": "deu"}]
    de_rows = query(service, prop, start, end, filters=de_filter).get("rows", [])
    de_summary = summarize(de_rows)

    # 3. Top 20 queries by impressions (global)
    q_rows = query(
        service, prop, start, end, dimensions=["query"], row_limit=20
    ).get("rows", [])
    top_queries = [
        {
            "query": r["keys"][0],
            "impressions": r.get("impressions", 0),
            "clicks": r.get("clicks", 0),
            "position": round(r.get("position", 0), 1),
            "ctr": round(r.get("ctr", 0), 4),
        }
        for r in q_rows
    ]

    # 4. Top 10 pages by impressions (global)
    p_rows = query(
        service, prop, start, end, dimensions=["page"], row_limit=10
    ).get("rows", [])
    top_pages = [
        {
            "page": r["keys"][0],
            "impressions": r.get("impressions", 0),
            "clicks": r.get("clicks", 0),
            "position": round(r.get("position", 0), 1),
        }
        for r in p_rows
    ]

    return {
        "property": prop,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": days,
        "global": global_summary,
        "germany": de_summary,
        "top_queries": top_queries,
        "top_pages": top_pages,
    }


def print_human(data):
    g, de = data["global"], data["germany"]
    print(f"GSC report — {data['property']}")
    print(f"Window: {data['start']} → {data['end']} ({data['days']} day(s))")
    print()
    print(f"  Global   impressions: {g['impressions']:>6}  clicks: {g['clicks']:>4}  "
          f"avg pos: {g['avg_position']}  ctr: {g['ctr']*100:.2f}%")
    print(f"  Germany  impressions: {de['impressions']:>6}  clicks: {de['clicks']:>4}  "
          f"avg pos: {de['avg_position']}  ctr: {de['ctr']*100:.2f}%")
    print()
    if data["top_queries"]:
        print("Top queries:")
        for q in data["top_queries"][:10]:
            print(f"  {q['impressions']:>5} impr · pos {q['position']:>4} · {q['query']}")
    else:
        print("Top queries: (none — site may be too new or have no impressions yet)")
    print()
    if data["top_pages"]:
        print("Top pages:")
        for p in data["top_pages"][:10]:
            print(f"  {p['impressions']:>5} impr · pos {p['position']:>4} · {p['page']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=1, help="lookback window in days")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args()
    data = fetch(days=args.days)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_human(data)


if __name__ == "__main__":
    main()
