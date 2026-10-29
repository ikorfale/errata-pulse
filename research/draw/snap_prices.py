"""Snapshot Manifold probabilities of all 445 candidates at the beacon round, sealed.

Runs once at 2026-10-31 12:00 UTC (systemd timer). Writes prices_at_round.json and prints only its sha256,
so the crowd benchmark for the five drawn questions is the price at the round, not whenever I look.
I do not open the file until my five forecasts are hashed and stamped (DRAW.md step 6).
"""
import hashlib, json, sys, time, urllib.request
from datetime import datetime, timezone

cands = json.load(open("candidates.json"))["candidates"]
out = {"taken_start": datetime.now(timezone.utc).isoformat(timespec="seconds"), "prices": {}}
for c in cands:
    try:
        req = urllib.request.Request(f"https://api.manifold.markets/v0/market/{c['id']}",
                                     headers={"User-Agent": "errata-draw/1 (errata@agentmail.to)"})
        m = json.load(urllib.request.urlopen(req, timeout=20))
        out["prices"][c["id"]] = {"p": m.get("probability"), "resolution": m.get("resolution"),
                                  "isResolved": m.get("isResolved")}
    except Exception as e:
        out["prices"][c["id"]] = {"error": str(e)[:120]}
    time.sleep(0.25)
out["taken_end"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
blob = json.dumps(out, sort_keys=True, separators=(",", ":")).encode()
open("prices_at_round.json", "wb").write(blob)
print(hashlib.sha256(blob).hexdigest(), file=sys.stdout)
