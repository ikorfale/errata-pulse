#!/usr/bin/env python3
"""Daily snapshot of Polymarket's holdingRewardsEnabled flag.

The Gamma API exposes only the current flag, no history, and the eligible list changes. A cohort-2 comparison
needs the flag on each quote date (yuigui, Moltbook 21.10), so the history has to be recorded as it happens.
Appends one line per run to poly_reward/snapshots.jsonl: scanned count, ids and questions with the flag on, and
what changed since the previous line (gained, lost while still open, no longer open).
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
            on.append({"id": m["id"], "q": m.get("question", "")[:120], "end": (m.get("endDate") or "")[:10],
                       "created": (m.get("createdAt") or "")[:16]})
    cursor = d.get("next_cursor")
    if not cursor or not d.get("events"):
        break
    time.sleep(0.5)
# Moltbook 22.10: does the record catch markets that LOSE the flag mid-life? The scan sees open markets only, so a
# flagged id missing today is either still open with the flag off (lost) or no longer open (closed or delisted).
prev, prev_ts = set(), None
if os.path.exists(OUT):
    with open(OUT) as f:
        lines = f.read().splitlines()
    if lines:
        last = json.loads(lines[-1])
        prev, prev_ts = {m["id"] for m in last["markets"]}, last["ts"]
now_on = {m["id"] for m in on}
gone = prev - now_on
rec = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "scanned": scanned,
       "pages": page, "enabled": len(on), "markets": on,
       "since_prev": {"gained": sorted(now_on - prev) if prev else None,
                      "lost_flag_still_open": sorted(gone & seen), "not_open_now": sorted(gone - seen)}}
# Moltbook 24.10 (yuigui): a listing rule flags only at birth; a curator can flag a market weeks old. Split the gains
# by createdAt against the previous snapshot time. One "flagged_old" settles it (PREREG-flag-diff.md).
if prev and prev_ts:
    created = {m["id"]: m["created"] for m in on}
    pts = prev_ts.replace("Z", "")
    rec["since_prev"]["gained_born_since_prev"] = sorted(i for i in now_on - prev if created.get(i, "") > pts)
    rec["since_prev"]["gained_flagged_old"] = sorted(i for i in now_on - prev if not created.get(i, "") > pts)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "a") as f:
    f.write(json.dumps(rec) + "\n")
print(rec["ts"], "scanned", scanned, "enabled", len(on), {k: (len(v) if v is not None else None) for k, v in rec["since_prev"].items()})
