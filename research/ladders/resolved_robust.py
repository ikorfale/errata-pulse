"""Exploratory, NOT preregistered (written 2026-10-30 after resolved_verdict.py had run): the same bins under the filter
behind the open-ladder "about two weeks" figure (censor_check.py: peak >= 0.05 and lasting >= 1 day; also >= 1 hour; the 7-day
opening-price exclusion is not applied here, market creation times were not fetched). Also P2 with more decimals and
a family-cluster bootstrap of the <7 vs 180-365 KM-median gap. Run: python3 resolved_robust.py"""
import json, random
from collections import defaultdict
from statistics import median

rows = [json.loads(l) for l in open('resolved/episodes.jsonl')]
BINS = [(0, 7, '<7'), (7, 30, '7-30'), (30, 180, '30-180'), (180, 365, '180-365'), (365, 1e9, '>365')]


def km_median(eps):
    s, n = 1.0, len(eps)
    for t, ev in sorted((e['heal'], not e['expired']) for e in eps):
        if ev:
            s *= (n - 1) / n
            if s <= 0.5:
                return t
        n -= 1
    return None


def table(rs, label):
    print(f'== {label}: {len(rs)} episodes, {len({r["family"] for r in rs})} families, expired {sum(r["expired"] for r in rs)}')
    for lo, hi, name in BINS:
        b = [r for r in rs if lo <= r['ttc'] < hi]
        if not b: print(name, 'empty'); continue
        h = [r for r in b if not r['expired']]
        fams = defaultdict(int)
        for r in b: fams[r['family']] += 1
        km = km_median(b)
        print(f'{name:>8} n {len(b):4} fam {len(fams):3} top {max(fams.values())/len(b):.2f} KM median '
              f'{km if km is None else round(km * 24, 2)} h  heal/ttc median {median(r["heal"]/r["ttc"] for r in h if r["ttc"] > 0):.2e}'
              f'  expired {sum(r["expired"] for r in b)/len(b):.3f}')


table(rows, 'all episodes (preregistered population)')
rob = [r for r in rows if r['peak'] >= 0.05 and (r['expired'] or r['heal'] >= 1 / 24)]
table(rob, 'robust: peak >= 0.05, >= 1 h')
day = [r for r in rows if r['peak'] >= 0.05 and r['heal'] >= 1]
table(day, 'open-ladder cut: peak >= 0.05, >= 1 day (KM still in hours)')

# family bootstrap: KM median(180-365) - KM median(<7), all episodes and robust
random.seed(20261030)
for lab, rs in (('all', rows), ('robust 1h', rob), ('cut 1d', day)):
    fam = defaultdict(list)
    for r in rs: fam[r['family']].append(r)
    keys = list(fam); d = []
    for _ in range(1000):
        s = [r for k in random.choices(keys, k=len(keys)) for r in fam[k]]
        a = km_median([r for r in s if r['ttc'] < 7]); b = km_median([r for r in s if 180 <= r['ttc'] < 365])
        if a is not None and b is not None: d.append((b - a) * 24)
    d.sort()
    print(f'{lab}: KM median 180-365 minus <7, hours: family bootstrap 95% {d[int(.025*len(d))]:.2f} .. {d[int(.975*len(d))-1]:.2f} ({len(d)} of 1000 draws defined)')
