"""glitchfox 107546: is 'clean pairs heal slower (14.3 vs 8.7 d)' a censoring artefact? Per class (criteria_pairs.json:
same vs near+differs) on the robust cut: open episodes, Kaplan-Meier median and survival at 7/14/30 d (open = censored at
now), and a split by time from episode start to the earlier rung's close. Written 29.10 ~11:14 UTC (date -u) after the question."""
import json, gzip
from statistics import median
D = 86400000
rows = [json.loads(l) for l in open('replay/episodes.jsonl')]
fam = json.load(open('replay/ladders-2026-10-29.json'))['families']
byurl = {m['url']: m for ms in fam.values() for m in ms}
first = {}
def start(u):
    i = byurl[u]['id']
    if i not in first:
        b = json.load(gzip.open(f'replay/bets/{i}.json.gz')); first[i] = b[0][0] if b else None
    return first[i]
k = [r for r in rows if r['start'] >= max(start(r['early']) or 0, start(r['late']) or 0) + 7 * D and r['peak'] >= .05 and r['days'] >= 1]
cls = {(a, b): c for a, b, c in json.load(open('replay/criteria_pairs.json'))}
def km(eps):
    t = sorted((r['days'], r['end'] is not None) for r in eps); n = len(t); s = 1.0; out = {}; med = None; i = 0
    while i < len(t):
        x = t[i][0]; d = c = 0
        while i < len(t) and t[i][0] == x: d += t[i][1]; c += 1; i += 1
        if d: s *= 1 - d / n
        n -= c
        for h in (7, 14, 30):
            if x <= h: out[h] = s
        if med is None and s <= .5: med = x
    return med, out
for name, sel in (('clean (same text)', lambda c: c == 'same'), ('mixed (near+differs)', lambda c: c != 'same')):
    e = [r for r in k if sel(cls[(r['early'], r['late'])])]
    m, s = km(e)
    surv = {h: sum(r['days'] > h for r in e) / len(e) for h in (7, 14, 30)}   # no open long enough to matter? check below
    print(f"{name}: episodes {len(e)}, open {sum(r['end'] is None for r in e)}, closed median {median(r['days'] for r in e if r['end']):.1f} d, "
          f"KM median {m:.1f} d, still broken at 7/14/30 d: " + "/".join(f"{surv[h]:.2f}" for h in (7, 14, 30)))
    for lo, hi, lab in ((0, 180, '<180 d'), (180, 365, '180-365 d'), (365, 730, '1-2 y'), (730, 1e9, '>2 y')):
        g = [r for r in e if lo <= (byurl[r['early']]['close'] - r['start']) / D < hi]
        if g: print(f"   earlier rung closes {lab} after episode start: n {len(g)}, median heal {median(r['days'] for r in g):.1f} d")
# mixed without the AGI family (514 of its episodes), and clean by family size, so one family does not set the median
e = [r for r in k if cls[(r['early'], r['late'])] != 'same' and not r['family'].startswith('will we get agi')]
print(f"mixed without AGI family: episodes {len(e)}, median heal {median(r['days'] for r in e):.1f} d, families {len({r['family'] for r in e})}")
from collections import Counter
for name, c0 in (('clean', 'same'),):
    e = [r for r in k if cls[(r['early'], r['late'])] == c0]; fc = Counter(r['family'] for r in e)
    print(f"{name}: families {len(fc)}, top 3 " + ", ".join(f"{f[:40]} {n}" for f, n in fc.most_common(3)))
    big = fc.most_common(1)[0][0]; e2 = [r for r in e if r['family'] != big]
    print(f"   without its biggest family: episodes {len(e2)}, median heal {median(r['days'] for r in e2):.1f} d")
    fm = sorted(median(r['days'] for r in e if r['family'] == f) for f in fc)
    print(f"   median of per-family medians: {median(fm):.1f} d over {len(fm)} families")
e = [r for r in k if cls[(r['early'], r['late'])] != 'same']; fc = Counter(r['family'] for r in e)
fm = sorted(median(r['days'] for r in e if r['family'] == f) for f in fc)
print(f"mixed: median of per-family medians {median(fm):.1f} d over {len(fm)} families")
