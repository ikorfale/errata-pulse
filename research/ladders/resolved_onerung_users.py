"""Bettor-level follow-up to resolved_onerung.py, preregistered in PREDICT-onerung-users-1030.md. Uses the refetch
with userId (resolved_fetch_users.py). Output: resolved/onerung_users.txt. Made by errata, an AI agent (https://errata.page)."""
import json, gzip, os, random, sys
from collections import defaultdict
CACHE = sys.argv[1]
TOL, H = 0.03, 3600000
fam = json.load(open('resolved/families.json'))['families']
def steps(i): return [tuple(x) for x in json.load(gzip.open(os.path.join(CACHE, i + '.json.gz')))]
rows = []; allbets = [0, 0]
for k, ms in fam.items():
    S = {m['id']: steps(m['id']) for m in ms}
    for i, e in enumerate(ms):
        for l in ms[i + 1:]:
            if l['close'] // 86400000 == e['close'] // 86400000: continue
            cut = e['end']
            ev = sorted([(b[0], 0, b) for b in S[e['id']] if b[0] <= cut] + [(b[0], 1, b) for b in S[l['id']] if b[0] <= cut],
                        key=lambda x: (x[0], x[1], x[2][1]))
            pa = pb = None; cur = None
            for t, r, b in ev:
                allbets[0] += 1; allbets[1] += b[3]
                if r == 0: pa = b[1]
                else: pb = b[1]
                if pa is None or pb is None: continue
                g = pa - pb
                if cur is not None and cur.get('first') is None and t > cur['start']:
                    cur.update(first=r, first_user=b[2], elapsed=t - cur['start'])
                if g > TOL:
                    if cur is None: cur = {'family': k, 'start': t, 'opener': r, 'user': b[2], 'api': b[3], 'peak': g, 'first': None}
                elif cur is not None:
                    cur.update(end=t, heal_rung=r, healer=b[2]); rows.append(cur); cur = None
            if cur is not None: cur['end'] = None; rows.append(cur)
def share(sub, cond, hit):
    x = [r for r in sub if cond(r)]
    return (sum(hit(r) for r in x) / len(x), len(x)) if x else (None, 0)
T = {
 'U1 opener-rung heals by the opening bettor': (lambda r: r['end'] and r['heal_rung'] == r['opener'], lambda r: r['healer'] == r['user']),
 'U3 first obs <1h on opener rung by the opening bettor': (lambda r: r['first'] is not None and r['elapsed'] < H and r['first'] == r['opener'], lambda r: r['first_user'] == r['user']),
 'U4 other-rung heals by the opening bettor': (lambda r: r['end'] and r['heal_rung'] != r['opener'], lambda r: r['healer'] == r['user']),
 'U2 breaks opened by an API bet': (lambda r: True, lambda r: r['api']),
}
fb = defaultdict(list)
for r in rows: fb[r['family']].append(r)
F = list(fb); rnd = random.Random(1030)
draws = [[r for g in rnd.choices(F, k=len(F)) for r in fb[g]] for _ in range(1000)]
out = [f'{len(rows)} episodes, {len(F)} families; API share of all bets on these pairs {allbets[1] / allbets[0]:.3f} ({allbets[0]} bet-pair rows)']
for name, (c, h) in T.items():
    s, n = share(rows, c, h)
    v = sorted(x for x in (share(d, c, h)[0] for d in draws) if x is not None)
    out.append(f'{name}: {s:.3f} of {n}, 95% {v[int(.025 * len(v))]:.3f} to {v[int(.975 * len(v))]:.3f}')
print('\n'.join(out)); open('resolved/onerung_users.txt', 'w').write('\n'.join(out) + '\n')
