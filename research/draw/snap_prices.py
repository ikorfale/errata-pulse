"""Snapshot Manifold probabilities of all 445 candidates at the beacon round, sealed.

Runs once at 2026-10-31 12:00 UTC (systemd timer). Writes prices_at_round.json and prints only its sha256,
so the crowd benchmark for the five drawn questions is the price at the round, not whenever I look.
I do not open the file until my five forecasts are hashed and stamped (DRAW.md step 6).
Second use (added 29.10 after gavinagent): `snap_prices.py --ids ID1,ID2,... -o prices_at_forecast.json` runs in the
same command that hashes forecasts.json, so the drawn five also get a crowd price from the moment my forecasts are
fixed. That later price is the primary benchmark (same information time as me); the round price is secondary.
"""
import argparse, hashlib, json, sys, time, urllib.request
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("--ids", default="")
ap.add_argument("-o", default="prices_at_round.json")
a = ap.parse_args()
cands = json.load(open("candidates.json"))["candidates"]
if a.ids:
    want = set(a.ids.split(","))
    cands = [c for c in cands if c["id"] in want]
    assert len(cands) == len(want), "unknown id"
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
open(a.o, "wb").write(blob)
print(hashlib.sha256(blob).hexdigest(), file=sys.stdout)
