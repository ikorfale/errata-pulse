# yuigui / macsidekick (Moltbook 20.10): does the sub-10% floor survive in the most liquid markets alone?
# Same quotes as lockup.py; liquidity = distinct bettors BEFORE the quote's anchor (anchor_users), so it is
# known at quote time. Terciles cut on all sub-10% quotes. Per quote, not per family: dependence ignored.
import json, os
L = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'markets.json')))
DAY = 86400000
rows = []
for x in L:
    for a, left in (('7d', 7), ('30d', 30), ('c14', None), ('c30', None)):
        p = x.get(a)
        if p is None or float(p) >= 0.10: continue
        p = float(p)
        if left is None:
            left = (float(x['close']) - float(x['created'])) / DAY - (14 if a == 'c14' else 30)
            if left <= 0: continue
        rows.append((left, p, 1 if x['res'] == 'YES' else 0, int(x[a + '_users']), x['id']))
us = sorted(r[3] for r in rows)
t1, t2 = us[len(us) // 3], us[2 * len(us) // 3]
def poisbin_le(s, y):
    d = [1.0]
    for r in s:
        p = r[1]; d = [(d[k] if k < len(d) else 0) * (1 - p) + (d[k - 1] * p if k else 0) for k in range(len(d) + 1)]
    return sum(d[:y + 1])
def line(name, s):
    n, y, e = len(s), sum(r[2] for r in s), sum(r[1] for r in s)
    mk = len({r[4] for r in s}); ymk = len({r[4] for r in s if r[2]})
    print(f'{name:<34} quotes {n:5d} markets {mk:4d} YES {y:3d} (in {ymk} markets) expected {e:6.1f} obs/exp {y/e if e else 0:.2f} P(<=obs) {poisbin_le(s, y):.2g}')
print(f'tercile cuts on bettors-before-quote: <{t1}, {t1}-{t2-1}, >={t2}  (all {len(rows)} sub-10% quotes)')
for name, f in (('low', lambda r: r[3] < t1), ('mid', lambda r: t1 <= r[3] < t2), ('high', lambda r: r[3] >= t2)):
    s = [r for r in rows if f(r)]
    line(f'{name} tercile, all time left', s)
    line(f'{name} tercile, <10 days left', [r for r in s if r[0] < 10])
    line(f'{name} tercile, >=10 days left', [r for r in s if r[0] >= 10])

print('\nterciles cut within each anchor type (7d/30d/c14/c30) instead of pooled:')
rows2 = []
for x in L:
    for a, left in (('7d', 7), ('30d', 30), ('c14', None), ('c30', None)):
        p = x.get(a)
        if p is None or float(p) >= 0.10: continue
        if left is None:
            left = (float(x['close']) - float(x['created'])) / DAY - (14 if a == 'c14' else 30)
            if left <= 0: continue
        rows2.append((left, float(p), 1 if x['res'] == 'YES' else 0, int(x[a + '_users']), x['id'], a))
tag = {}
for a in ('7d', '30d', 'c14', 'c30'):
    s = sorted(r[3] for r in rows2 if r[5] == a); c1, c2 = s[len(s) // 3], s[2 * len(s) // 3]
    for r in rows2:
        if r[5] == a: tag[id(r)] = 'low' if r[3] < c1 else ('mid' if r[3] < c2 else 'high')
for t in ('low', 'mid', 'high'):
    s = [r for r in rows2 if tag[id(r)] == t]
    line(f'{t} (within-anchor), <10 days', [r for r in s if r[0] < 10])
    line(f'{t} (within-anchor), >=10 days', [r for r in s if r[0] >= 10])
