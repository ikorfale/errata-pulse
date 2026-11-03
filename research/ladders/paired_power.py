"""#113027: paired (within-family) power at the real eligible counts, not a toy. For each adjacent time-to-close boundary,
take the families with healed episodes on both sides. Null: within each family, pool its A and B log heal times and
reassign them to sides at random keeping the real counts (real within-family spread, no distance effect); then the B side
is multiplied by r. Statistic: median over families of (median log heal B - median log heal A); test = 95% family-bootstrap
interval excluding 0. 400 datasets x 1000 draws, seed 113027; MC SE shown. Healed episodes only (as the s_b estimate).
Written 2026-11-03 (date -u). Run: python3 paired_power.py > resolved/paired_power.txt"""
import json, math
from collections import defaultdict
import numpy as np
rows = [json.loads(l) for l in open('resolved/episodes.jsonl')]
BINS = [(0, 7, '<7'), (7, 30, '7-30'), (30, 180, '30-180'), (180, 365, '180-365'), (365, 1e9, '>365')]
def b(t): return next(i for i, (lo, hi, _) in enumerate(BINS) if lo <= t < hi)
g = defaultdict(lambda: defaultdict(list))
for r in rows:
    if not r['expired'] and r['heal'] > 0: g[r['family']][b(r['ttc'])].append(math.log(r['heal']))
rng = np.random.default_rng(113027); ND, NB = 400, 1000
def power(fams, r):
    hits = 0
    for _ in range(ND):
        d = []
        for a, bb in fams:
            pool = rng.permutation(np.r_[a, bb]); A, B = pool[:len(a)], pool[len(a):] + math.log(r)
            d.append(np.median(B) - np.median(A))
        d = np.array(d); bs = np.median(d[rng.integers(0, len(d), (NB, len(d)))], axis=1)
        lo, hi = np.percentile(bs, [2.5, 97.5]); hits += (lo > 0) or (hi < 0)
    p = hits / ND; return p, math.sqrt(p * (1 - p) / ND)
print('boundary          min eps/side  families  power r=1 (FP)   power x2        power x3')
for i in range(4):
    for k in (1, 3):
        fams = [(np.array(v[i]), np.array(v[i + 1])) for v in g.values() if len(v.get(i, [])) >= k and len(v.get(i + 1, [])) >= k]
        if len(fams) < 3: print(f'{BINS[i][2]:>7} | {BINS[i+1][2]:<8} {k:>6}  {len(fams):>8}  -'); continue
        out = [power(fams, r) for r in (1, 2, 3)]
        print(f'{BINS[i][2]:>7} | {BINS[i+1][2]:<8} {k:>6}  {len(fams):>8}  ' + '  '.join(f'{p:.3f}±{s:.3f}' for p, s in out))
