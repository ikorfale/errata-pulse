"""#113005/#113007: before a paired (within-family) design for P1, count the families and the rung pairs that have
episodes on both sides of each adjacent time-to-close boundary, and estimate the between-family spread s_b of log
heal time (method of moments on healed episodes: var of family means minus mean within-variance / n_f).
Unit of heal: days. Written 2026-11-03 (date -u). Run: python3 paired_eligible.py > resolved/paired_eligible.txt"""
import json, math, statistics as st
from collections import defaultdict
rows = [json.loads(l) for l in open('resolved/episodes.jsonl')]
BINS = [(0, 7, '<7'), (7, 30, '7-30'), (30, 180, '30-180'), (180, 365, '180-365'), (365, 1e9, '>365')]
def b(t): return next(i for i, (lo, hi, _) in enumerate(BINS) if lo <= t < hi)
for unit in ('family', 'pair'):
    key = (lambda r: r['family']) if unit == 'family' else (lambda r: (r['early'], r['late']))
    g = defaultdict(lambda: defaultdict(int))
    for r in rows: g[key(r)][b(r['ttc'])] += 1
    print(f'== unit: {unit} (total {len(g)}; in 1 bin only: {sum(1 for v in g.values() if len(v) == 1)})')
    print('boundary            both sides  >=3 eps each side  median eps (A/B) among both')
    for i in range(4):
        both = [v for v in g.values() if v.get(i) and v.get(i + 1)]
        three = sum(1 for v in both if v[i] >= 3 and v[i + 1] >= 3)
        ma = st.median([v[i] for v in both]) if both else '-'; mb = st.median([v[i + 1] for v in both]) if both else '-'
        print(f'{BINS[i][2]:>7} | {BINS[i+1][2]:<8} {len(both):>10}  {three:>17}  {ma}/{mb}')
# s_b on log(heal) of healed episodes, within each bin (family effect net of distance)
print('\n== between-family SD of log heal time (healed episodes, families with >=2 in the bin)')
print('bin        fams  s_within  s_between(MoM)')
for i, (lo, hi, nm) in enumerate(BINS):
    f = defaultdict(list)
    for r in rows:
        if lo <= r['ttc'] < hi and not r['expired'] and r['heal'] > 0: f[r['family']].append(math.log(r['heal']))
    f = [v for v in f.values() if len(v) >= 2]
    if len(f) < 3: print(f'{nm:<9} {len(f):>4}  -'); continue
    w = st.mean(st.variance(v) for v in f); means = [st.mean(v) for v in f]
    sb2 = st.variance(means) - st.mean(st.variance(v) / len(v) for v in f)
    print(f'{nm:<9} {len(f):>4}  {math.sqrt(w):8.2f}  {math.sqrt(max(sb2, 0)):8.2f}')
