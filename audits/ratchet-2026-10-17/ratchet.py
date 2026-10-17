#!/usr/bin/env python3
"""Is the Chaos Pulse a ratchet?  Three checks on my own index, from its own files.

1. Moves: for every component, how many report-to-report moves went up, down, flat.
2. Ledger: does the event ledger ever end anything?  Share of events with a re-check date,
   re-checks already overdue, events marked ended/refuted/disputed.
3. Outside: my daily index against the Caldara-Iacoviello daily geopolitical risk index (GPRD,
   matteoiacoviello.com, data_gpr_daily_recent.xls) on the days both exist.

Run: PULSE_DIR=<pulse folder> python ratchet.py  (gpr_daily.xls from matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls)
     [today YYYY-MM-DD]   -> prints result, writes ratchet.png
"""
import json, sys, datetime as dt, collections
import xlrd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.environ.get("PULSE_DIR", os.path.join(HERE, "pulse")) + "/"  # folder with history.jsonl, events.jsonl
today = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
COMP = ["military", "energy", "economy", "institutions", "restraint"]

hist = [json.loads(l) for l in open(P + "history.jsonl")]
print(f"reports: {len(hist)}  {hist[0]['ts'][:10]} .. {hist[-1]['ts'][:10]}")
print(f"index: {hist[0]['ph']} -> {hist[-1]['ph']}")

# 1. moves
tot = collections.Counter()
for c in COMP:
    m = collections.Counter()
    for a, b in zip(hist, hist[1:]):
        d = b["components"][c] - a["components"][c]
        m["up" if d > 0 else "down" if d < 0 else "flat"] += 1
        if d:
            m["sum_up" if d > 0 else "sum_down"] += abs(d)
    tot.update(m)
    print(f"  {c:12s} up {m['up']:2d} (+{m['sum_up']})  down {m['down']:2d} (-{m['sum_down']})  flat {m['flat']:2d}"
          f"   {hist[0]['components'][c]} -> {hist[-1]['components'][c]}")
print(f"  all moves: up {tot['up']}  down {tot['down']}  flat {tot['flat']}   points +{tot['sum_up']} / -{tot['sum_down']}")
ph = [h["ph"] for h in hist]
pm = collections.Counter("up" if b > a else "down" if b < a else "flat" for a, b in zip(ph, ph[1:]))
print(f"  index moves: up {pm['up']}  down {pm['down']}  flat {pm['flat']}")
# sign test: of the non-flat component moves, chance of <= down under p=0.5
from math import comb
n = tot["up"] + tot["down"]; k = tot["down"]
p = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
print(f"  sign test (non-flat component moves, H0 up=down): {k} down of {n}, one-sided p = {p:.2g}")

# 2. ledger
ev = [json.loads(l) for l in open(P + "events.jsonl")]
st = collections.Counter(e["status"] for e in ev)
ended = [e for e in ev if e.get("state") == "ended" or e.get("active") is False
         or any(w in (e.get("update") or "").lower() for w in ("ended", "закончил", "завершен", "завершён", "возобнов", "восстановлен"))]
withre = [e for e in ev if e.get("recheck")]
overdue = [e for e in withre if e["recheck"] < today and e["status"] in ("confirmed", "claimed")]
counted = [e for e in ev if e.get("counted_in")]
once = [e for e in counted if len(e["counted_in"]) == 1]
print(f"events: {len(ev)}  status {dict(st)}")
print(f"  with a re-check date: {len(withre)} ({100*len(withre)/len(ev):.0f}%)   overdue on {today}: {len(overdue)}")
print(f"  words of ending/recovery in status or update: {len(ended)}")
print(f"  counted in exactly one report: {len(once)} of {len(counted)}")
bycomp = collections.Counter(e["component"] for e in ev)
print(f"  by component: {dict(bycomp)}")

# 3. outside: GPRD
s = xlrd.open_workbook(os.path.join(HERE, "gpr_daily.xls")).sheet_by_index(0)
g = {}
for r in range(1, s.nrows):
    v = s.row_values(r)
    d = str(v[0])[:8]
    g[f"{d[:4]}-{d[4:6]}-{d[6:8]}"] = (v[2], v[7])  # GPRD, GPRD_MA7
mine = {h["ts"][:10]: h["ph"] for h in hist if h["kind"] != "initial"}
both = sorted(set(mine) & set(g))
print(f"GPRD last day: {max(g)}   overlap with my daily reports: {len(both)} days {both[0]}..{both[-1]}")
x = np.array([mine[d] for d in both], float); y7 = np.array([g[d][1] for d in both])
print(f"  my index {x[0]:.0f} -> {x[-1]:.0f};  GPRD 7-day mean {y7[0]:.0f} -> {y7[-1]:.0f}")
if len(both) > 3:
    r = np.corrcoef(np.diff(x), np.diff(y7))[0, 1]
    print(f"  corr of daily changes (mine vs GPRD MA7): {r:+.2f} on {len(both)-1} changes")
yr = [v[0] for k, v in g.items() if k.startswith("2026")]
win = [g[d][0] for d in both]
pct = np.mean([w <= np.percentile(yr, 50) for w in win])
print(f"  GPRD 2026 mean {np.mean(yr):.0f}; overlap-window mean {np.mean(win):.0f}; window days at/below the 2026 median: {pct:.0%}")

# chart: two panels, same dates, no dual axis
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, gridspec_kw={"height_ratios": [1, 1]})
days = sorted(k for k in g if k >= "2026-09-01")
md = sorted(mine)
ax.step([dt.date.fromisoformat(d) for d in md], [mine[d] for d in md], where="post", color="#b2182b", lw=2.5)
ax.plot([dt.date.fromisoformat(d) for d in md], [mine[d] for d in md], "o", color="#b2182b", ms=4)
ax.set_ylabel("Chaos Pulse (0-100)")
ax.set_title("Mine: 6 steps up, 0 down in 12 reports", loc="left", fontsize=11)
ax2.plot([dt.date.fromisoformat(d) for d in days], [g[d][1] for d in days], color="#555", lw=1.8)
ax2.set_ylabel("GPRD, 7-day mean")
ax2.set_title(f"Outside: Caldara-Iacoviello daily geopolitical risk (to {max(g)}), up and down", loc="left", fontsize=11)
for a in (ax, ax2):
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
    a.axvspan(dt.date.fromisoformat(md[0]), dt.date.fromisoformat(md[-1]), color="#eee", zorder=0)
fig.suptitle("Is my crisis index a ratchet?", fontsize=13, x=0.01, ha="left")
fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(os.path.join(HERE, "gpr_vs_mine.png"), dpi=130)
print("chart: gpr_vs_mine.png (lab only; GPR is a flow measure, not a fair benchmark)")
