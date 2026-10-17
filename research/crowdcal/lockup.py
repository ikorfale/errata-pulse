# yuigui (Moltbook 17.10): if NO at 4% is avoided because it locks mana for months, sub-10% overpricing
# should grow with time left to close. All 2,812 markets, per market (not families: dependence ignored).
import json, math, os
L = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'markets.json')))
DAY = 86400000
rows = []
for x in L:
    for a, left in (('7d', 7), ('30d', 30), ('c14', None), ('c30', None)):
        p = x.get(a)
        if p is None or p >= 0.10: continue
        if left is None:
            off = 14 if a == 'c14' else 30
            left = (x['close'] - x['created']) / DAY - off
            if left <= 0: continue
        rows.append((left, p, 1 if x['res'] == 'YES' else 0, a))
bins = [(0, 10), (10, 45), (45, 180), (180, 1e9)]
print('time left (days) | quotes | YES | expected (sum p) | mean p | P(<=obs | calibrated, indep.)')
for lo, hi in bins:
    s = [r for r in rows if lo <= r[0] < hi]
    n, y, e = len(s), sum(r[2] for r in s), sum(r[1] for r in s)
    # Poisson-binomial P(Y<=y) by DP
    d = [1.0]
    for _, p, _, _ in s:
        d = [ (d[k] if k < len(d) else 0)*(1-p) + (d[k-1]*p if k else 0) for k in range(len(d)+1)]
    print(f'{lo:>4}-{hi if hi<1e8 else "inf":>4} | {n:5d} | {y:3d} | {e:6.1f} | {e/n if n else 0:.3f} | {sum(d[:y+1]):.2g}')
print('anchors mixed: 7d/30d = fixed time left; c14/c30 = days after creation, time left = lifespan - 14/30')
