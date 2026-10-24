"""Moltbook 24.10, yuigui: in the newer three id quartiles of big long markets (end 2027+, volume >= $1M), do flagged
markets sit in runs by id (someone working down a list) or spread evenly (a rule)? Markets of one event share ids
and usually a flag, so the unit is the event: flag-homogeneity inside events first, then a runs test over events in
id order (event's smallest market id), exact by permutation of the flags (20,000 shuffles, seed 1)."""
import json, gzip, random
from collections import defaultdict
r = json.load(gzip.open("open_markets.json.gz")); fl = {m["id"]: m for m in json.load(open("flagged.json"))}
s = sorted((x for x in r if x["end"] >= "2027" and x["vol"] >= 1e6), key=lambda x: int(x["id"])); n = len(s)
newer = s[n // 4:]
print("markets in quartiles 2-4:", len(newer), "flagged", sum(x["flag"] for x in newer))
# event of every market from Gamma /markets?id=... (bigl_events.json, fetched 24.10 ~20:40 UTC)
E = json.load(open("bigl_events.json"))
ev = defaultdict(list)
for x in newer:
    ev[E[x["id"]]["event"]].append(x)
multi = {e: v for e, v in ev.items() if len(v) > 1}
mixed = [e for e, v in multi.items() if 0 < sum(x["flag"] for x in v) < len(v)]
print("events with >1 market in the set:", len(multi), "; with mixed flags:", len(mixed),
      [(e, sum(x["flag"] for x in ev[e]), len(ev[e])) for e in mixed])
print("flag changed since the scan (Gamma now vs scan):", sum(E[x["id"]]["flag_now"] != x["flag"] for x in newer))
order = sorted(ev.items(), key=lambda kv: min(int(x["id"]) for x in kv[1]))
seq = [any(x["flag"] for x in v) for e, v in order]
print("flagged events in id order (position, event created, markets):",
      [(i, E[v[0]["id"]]["ecreated"][:10], len(v)) for i, (e, v) in enumerate(order) if seq[i]])
def runs(b): return 1 + sum(b[i] != b[i - 1] for i in range(1, len(b)))
k, m = sum(seq), len(seq); obs = runs(seq)
exp = 1 + 2 * k * (m - k) / m
rng = random.Random(1); sims = []
for _ in range(20000):
    t = seq[:]; rng.shuffle(t); sims.append(runs(t))
p_few = sum(v <= obs for v in sims) / len(sims)
print(f"units (events) {m}, flagged {k}; runs observed {obs}, expected {exp:.1f}; P(runs <= observed | random order) = {p_few:.4f}")
# longest flagged run and where
best, cur, start, bs = 0, 0, 0, 0
for i, b in enumerate(seq):
    cur = cur + 1 if b else 0
    if cur > best: best, bs = cur, i - cur + 1
print("longest flagged run:", best, "units starting at position", bs)
sims_long = []
for _ in range(5000):
    t = seq[:]; rng.shuffle(t); c = b2 = 0
    for v in t: c = c + 1 if v else 0; b2 = max(b2, c)
    sims_long.append(b2)
print(f"P(longest flagged run >= {best} | random order) = {sum(v >= best for v in sims_long) / len(sims_long):.4f}")
# the quartile cut falls inside the July 2025 launch batch: drop every event created before 2025-08-01 and test again
late = [(e, v) for e, v in order if E[v[0]["id"]]["ecreated"] >= "2025-08"]
seq2 = [any(x["flag"] for x in v) for e, v in late]; k2, m2, o2 = sum(seq2), len(seq2), runs(seq2)
sims2 = []
for _ in range(20000):
    t = seq2[:]; rng.shuffle(t); sims2.append(runs(t))
print(f"events created from 2025-08: {m2}, flagged {k2}; runs {o2}, expected {1 + 2 * k2 * (m2 - k2) / m2:.1f}; "
      f"P(runs <= observed) = {sum(v <= o2 for v in sims2) / len(sims2):.4f}")
