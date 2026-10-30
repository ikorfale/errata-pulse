"""glitchfox #108728: is the hour rise of heal time with ttc just liquidity? Re-measure each resolved-ladder episode
in trades: bets on either rung in (start, end] (expired: up to the early rung's end, censored). Also the pair's
trade rate in the 7 days before the break, and heal in units of that pair's own mean inter-trade gap.
Same bins, KM (expired censored), family bootstrap of the <7 -> 180-365 gap. Exploratory, not preregistered."""
import json, gzip, random
from bisect import bisect_right, bisect_left
from collections import defaultdict
fam = json.load(open('resolved/families.json'))['families']
uid = {m['url']: m['id'] for ms in fam.values() for m in ms}
T = {}
def times(url):
    i = uid[url]
    if i not in T: T[i] = sorted(t for t, _ in json.load(gzip.open(f'resolved/bets/{i}.json.gz')))
    return T[i]
def count(ts, a, b): return bisect_right(ts, b) - bisect_right(ts, a)
D, W = 86400000, 7 * 86400000
rows = []
for l in open('resolved/episodes.jsonl'):
    r = json.loads(l); a, b = times(r['early']), times(r['late'])
    end = r['start'] + r['heal'] * D
    r['trades'] = count(a, r['start'], end) + count(b, r['start'], end)
    pre = count(a, r['start'] - W, r['start']) + count(b, r['start'] - W, r['start'])
    r['rate_h'] = pre / (7 * 24)                      # trades per hour on the pair, week before the break
    r['heal_gaps'] = r['heal'] * 24 * r['rate_h'] if pre else None   # heal in units of the mean gap
    rows.append(r)
BINS = [(0, 7, '<7'), (7, 30, '7-30'), (30, 180, '30-180'), (180, 365, '180-365'), (365, 1e9, '>365')]
def km(eps, key):
    s, n = 1.0, len(eps)
    for t, ev in sorted((e[key], not e['expired']) for e in eps if e[key] is not None):
        if ev:
            s *= (n - 1) / n
            if s <= .5: return t
        n -= 1
def med(x): x = sorted(x); return x[len(x) // 2] if x else None
def table(sub, label):
    print(f'\n{label}: {len(sub)} episodes')
    print('ttc bin     n  fams  KM heal h  KM trades  median rate/h  KM heal/gap')
    for lo, hi, nm in BINS:
        b = [r for r in sub if lo <= r['ttc'] < hi]
        if not b: continue
        h = km(b, 'heal'); g = [r for r in b if r['heal_gaps'] is not None]
        print(f"{nm:8}{len(b):6}{len({r['family'] for r in b}):5}{(h or 0)*24:10.2f}{km(b, 'trades') or 0:10}"
              f"{med([r['rate_h'] for r in b]):14.2f}{(km(g, 'heal_gaps') or 0):12.2f}")
    fb = defaultdict(list)
    for r in sub: fb[r['family']].append(r)
    F = list(fb); rnd = random.Random(1030); res = {'trades': [], 'heal_gaps': []}
    for _ in range(1000):
        s = [r for f in rnd.choices(F, k=len(F)) for r in fb[f]]
        lo = [r for r in s if r['ttc'] < 7]; hi = [r for r in s if 180 <= r['ttc'] < 365]
        for k in res:
            x, y = km([r for r in lo if r[k] is not None], k), km([r for r in hi if r[k] is not None], k)
            if x is not None and y is not None: res[k].append(y - x)
    for k, v in res.items():
        v.sort(); print(f'  gap 180-365 minus <7 in {k}: 95% {v[int(.025*len(v))]:+.2f} to {v[int(.975*len(v))]:+.2f} ({len(v)} draws)')
table(rows, 'all episodes (preregistered population)')
table([r for r in rows if r['peak'] >= .05 and r['heal'] >= 1], 'lasting breaks (peak>=0.05, >=1 day)')
