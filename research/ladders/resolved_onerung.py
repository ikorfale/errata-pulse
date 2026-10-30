"""glitchfox #108782, preregistered in PREDICT-onerung-1030.md: which rung heals a ladder break? Rebuilds the episodes
of resolved_ladders.py from the cached bet steps, keeping which rung each trade was on. Bet cache: resolved/bets
(local, see resolved_ladders.py). Output: resolved/onerung.txt. Made by errata, an AI agent (https://errata.page)."""
import json, gzip, os, random, sys
from collections import defaultdict
CACHE = sys.argv[1] if len(sys.argv) > 1 else 'resolved/bets'
TOL, H = 0.03, 3600000
fam = json.load(open('resolved/families.json'))['families']
def steps(i): return json.load(gzip.open(os.path.join(CACHE, i + '.json.gz')))
rows = []
for k, ms in fam.items():
    S = {m['id']: steps(m['id']) for m in ms}
    for i, e in enumerate(ms):
        for l in ms[i + 1:]:
            if l['close'] // 86400000 == e['close'] // 86400000: continue
            cut = e['end']
            ev = sorted([(t, 0, p) for t, p in S[e['id']] if t <= cut] + [(t, 1, p) for t, p in S[l['id']] if t <= cut])
            pa = pb = None; cur = None
            for t, r, p in ev:
                if r == 0: pa = p
                else: pb = p
                if pa is None or pb is None: continue
                g = pa - pb
                if cur is not None and cur.get('first') is None and t > cur['start']:
                    cur['first'] = r; cur['first_heal'] = g <= TOL; cur['elapsed'] = t - cur['start']
                if cur is not None and t > cur['start']: cur['n'][r] += 1
                if g > TOL:
                    if cur is None: cur = {'family': k, 'start': t, 'opener': r, 'peak': g, 'first': None, 'n': [0, 0]}
                    else: cur['peak'] = max(cur['peak'], g)
                elif cur is not None:
                    cur['end'] = t; cur['heal_rung'] = r; rows.append(cur); cur = None
            if cur is not None: cur['end'] = None; rows.append(cur)
for r in rows:
    r['heal_d'] = ((r['end'] or 0) - r['start']) / 86400000 if r['end'] else None
    if r['first'] is not None: r['cls'] = 'same' if r['first'] == r['opener'] else 'other'
STR = [(0, H, '<1h'), (H, 24 * H, '1-24h'), (24 * H, 1e18, '>=24h')]
def p1(sub):
    tot, acc, cells = 0, 0.0, []
    for lo, hi, nm in STR:
        b = [r for r in sub if r.get('cls') and lo <= r['elapsed'] < hi]
        o = [r['first_heal'] for r in b if r['cls'] == 'other']; s = [r['first_heal'] for r in b if r['cls'] == 'same']
        po = sum(o) / len(o) if o else None; ps = sum(s) / len(s) if s else None
        cells.append((nm, len(o), po, len(s), ps))
        if o and s: acc += len(b) * (po - ps); tot += len(b)
    return (acc / tot if tot else None), cells
def p3(sub):
    h = [r for r in sub if r['end']]
    if not h: return None
    share_heal = sum(r['heal_rung'] != r['opener'] for r in h) / len(h)
    no = sum(r['n'][1 - r['opener']] for r in sub); na = sum(sum(r['n']) for r in sub)
    return share_heal - no / na, share_heal, no / na, len(h)
def boot(sub, f):
    fb = defaultdict(list)
    for r in sub: fb[r['family']].append(r)
    F = list(fb); rnd = random.Random(1030); v = []
    for _ in range(1000):
        x = f([r for g in rnd.choices(F, k=len(F)) for r in fb[g]])
        if x is not None: v.append(x)
    v.sort(); return v[int(.025 * len(v))], v[int(.975 * len(v))]
out = []
for lab, sub in [('all episodes', rows), ('lasting breaks (peak>=0.05, >=1 day)',
                 [r for r in rows if r['peak'] >= .05 and (r['heal_d'] is None or r['heal_d'] >= 1)])]:
    d, cells = p1(sub)
    out.append(f'\n{lab}: {len(sub)} episodes, {len({r["family"] for r in sub})} families, opener=early rung {sum(r["opener"]==0 for r in sub)}')
    out.append('stratum   n_other  P(heal|other)  n_same  P(heal|same)')
    for nm, no, po, ns, ps in cells:
        out.append(f'{nm:8}{no:9}{(po if po is not None else float("nan")):14.3f}{ns:8}{(ps if ps is not None else float("nan")):14.3f}')
    lo, hi = boot(sub, lambda s: p1(s)[0])
    out.append(f'P1 stratified other-minus-same: {d:+.3f}, 95% {lo:+.3f} to {hi:+.3f}')
    x = p3(sub); lo, hi = boot(sub, lambda s: (p3(s) or [None])[0])
    out.append(f'P3 heal by other rung {x[1]:.3f} of {x[3]} heals vs other-rung share of trades {x[2]:.3f}: {x[0]:+.3f}, 95% {lo:+.3f} to {hi:+.3f}')
print('\n'.join(out)); open('resolved/onerung.txt', 'w').write('\n'.join(out) + '\n')
