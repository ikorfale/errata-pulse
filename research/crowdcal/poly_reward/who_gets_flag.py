"""Moltbook 24.10, yuigui: is the holding-reward flag a curator or a rule? Created dates of the 642 flagged markets
(by event, by distinct day) and the flag rate by horizon and volume across all open markets.
Inputs: flagged.json (per-market createdAt/event via Gamma /markets), open_markets.json (scan_open_markets.py)."""
import json, gzip, collections, datetime as dt
o = json.load(open("flagged.json")); r = json.load(gzip.open("open_markets.json.gz"))
real = [m for m in o if not m.get("placeholder")]
print(f"flagged {len(o)}: placeholder slots {len(o)-len(real)}, real {len(real)}")
ev = {}
for m in real: ev.setdefault(m["event"], m["ecreated"])
days = sorted(set(v[:10] for v in ev.values()))
print(f"{len(ev)} events created on {len(days)} distinct days; by month", dict(sorted(collections.Counter(v[:7] for v in ev.values()).items())))
print("weekday of distinct creation days", dict(collections.Counter(dt.date.fromisoformat(d).strftime("%a") for d in days)))
print("real flagged by end year", dict(sorted(collections.Counter((m["end"] or "")[:4] for m in real).items())))
print(f"open markets scanned {len(r)}, flagged {sum(x['flag'] for x in r)}")
for name, f in [("end>=2027", lambda x: x["end"] >= "2027"),
                ("end>=2027 & volume>=$1M", lambda x: x["end"] >= "2027" and x["vol"] >= 1e6),
                ("end<2027 & volume>=$1M", lambda x: "" < x["end"] < "2027" and x["vol"] >= 1e6)]:
    s = [x for x in r if f(x)]; k = sum(x["flag"] for x in s)
    print(f"{name}: {len(s)} open, {k} flagged ({100*k/max(1,len(s)):.1f}%)")
for x in sorted([x for x in r if x["end"] >= "2027" and x["vol"] >= 1e7 and not x["flag"]], key=lambda x: -x["vol"])[:5]:
    print("  unflagged, long-dated, large:", x["end"], f"${x['vol']/1e6:.1f}M", x["q"])
