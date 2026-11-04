"""#113051 (glitchfox): same paired simulation as paired_power.py (same families, same within-family reshuffle null,
B side times r, 400 datasets, seed 113027), but the decision is an exact two-sided Wilcoxon signed-rank test on the
per-family differences (median log heal B - median log heal A), p < 0.05, instead of the family-bootstrap CI.
Zero differences dropped and counted (rule fixed before the run); tied |d| get average ranks, exact null by DP over
doubled ranks. Written 2026-11-04 (date -u). Run: python3 paired_power_wsr.py > resolved/paired_power_wsr.txt"""
import json, math
from collections import defaultdict
import numpy as np
rows = [json.loads(l) for l in open('resolved/episodes.jsonl')]
BINS = [(0, 7, '<7'), (7, 30, '7-30'), (30, 180, '30-180'), (180, 365, '180-365'), (365, 1e9, '>365')]
def b(t): return next(i for i, (lo, hi, _) in enumerate(BINS) if lo <= t < hi)
g = defaultdict(lambda: defaultdict(list))
for r in rows:
    if not r['expired'] and r['heal'] > 0: g[r['family']][b(r['ttc'])].append(math.log(r['heal']))
rng = np.random.default_rng(113027); ND = 400
def wsr_p(d):
    d = d[np.abs(d) > 1e-12]; n = len(d)
    if n == 0: return 1.0, 0
    a = np.abs(d); order = a.argsort(); rk = np.empty(n); i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(a[order[j + 1]] - a[order[i]]) < 1e-12: j += 1
        rk[order[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    r2 = np.rint(2 * rk).astype(int); tot = r2.sum(); dist = np.zeros(tot + 1); dist[0] = 1
    dist = np.zeros(tot + 1); dist[0] = 1
    for v in r2:
        new = dist.copy(); new[v:] += dist[:tot + 1 - v]; dist = new
    dist /= dist.sum(); w = int(np.rint(2 * rk[d > 0].sum())); cdf = np.cumsum(dist)
    p = 2 * min(cdf[w], 1 - (cdf[w - 1] if w > 0 else 0)); return min(p, 1.0), n
def power(fams, r):
    hits = 0; dropped = 0
    for _ in range(ND):
        d = []
        for a, bb in fams:
            pool = rng.permutation(np.r_[a, bb]); A, B = pool[:len(a)], pool[len(a):] + math.log(r)
            d.append(np.median(B) - np.median(A))
        p, n = wsr_p(np.array(d)); dropped += len(d) - n; hits += p < 0.05
    q = hits / ND; return q, math.sqrt(q * (1 - q) / ND), dropped / ND
print('boundary          min eps/side  families  WSR r=1 (FP)     WSR x2          WSR x3        mean zeros dropped (r=1)')
for i in range(4):
    for k in (1, 3):
        fams = [(np.array(v[i]), np.array(v[i + 1])) for v in g.values() if len(v.get(i, [])) >= k and len(v.get(i + 1, [])) >= k]
        if len(fams) < 3: print(f'{BINS[i][2]:>7} | {BINS[i+1][2]:<8} {k:>6}  {len(fams):>8}  -'); continue
        out = [power(fams, r) for r in (1, 2, 3)]
        print(f'{BINS[i][2]:>7} | {BINS[i+1][2]:<8} {k:>6}  {len(fams):>8}  ' + '  '.join(f'{p:.3f}±{s:.3f}' for p, s, _ in out) + f'  {out[0][2]:.2f}')
