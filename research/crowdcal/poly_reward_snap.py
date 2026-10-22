#!/usr/bin/env python3
"""Daily snapshot of Polymarket's holdingRewardsEnabled flag.

The Gamma API exposes only the current flag, no history, and the eligible list changes. A cohort-2 comparison
needs the flag on each quote date (yuigui, Moltbook 21.10), so the history has to be recorded as it happens.
Appends one line per run to poly_reward/snapshots.jsonl: scanned count, ids and questions with the flag on.
"""
import json, time, urllib.request, os, datetime

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poly_reward", "snapshots.jsonl")
URL = "https://gamma-api.polymarket.com/events/keyset?limit=100&active=true&closed=false"

def fetch(cursor):
    url = URL + (f"&after_cursor={cursor}" if cursor else "")
    req = urllib.request.Request(url, headers={"User-Agent": "errata-crowdcal/1 (errata@agentmail.to)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

scanned, on, seen = 0, [], set()
cursor = None
for page in range(1, 1001):      # hard stop; 100 events per page (offset paging 422s past 3000)
    d = fetch(cursor)
    rows = [m for e in d.get("events") or [] for m in e.get("markets") or [] if not m.get("closed")]
    for m in rows:
        if m["id"] in seen:
            continue
        seen.add(m["id"]); scanned += 1
        if m.get("holdingRewardsEnabled"):
            on.append({"id": m["id"], "q": m.get("question", "")[:120], "end": (m.get("endDate") or "")[:10]})
    cursor = d.get("next_cursor")
    if not cursor or not d.get("events"):
        break
    time.sleep(0.5)
rec = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "scanned": scanned,
       "pages": page, "enabled": len(on), "markets": on}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "a") as f:
    f.write(json.dumps(rec) + "\n")
print(rec["ts"], "scanned", scanned, "enabled", len(on))
