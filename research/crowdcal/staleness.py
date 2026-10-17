# yuigui (Moltbook 17.10): is the short-end long-shot excess a stale quote nobody bothers to sell?
# For every sub-10% quote with <10 days left to close, fetch the last bet before the anchor time and split
# by its age. Also: carry check from stored prices, 30d -> 7d drift of sub-10% markets.
import json, os, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, 'markets.json')))
D = 86400000
CACHE = os.path.join(HERE, 'staleness_cache.json')
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def last_bet(mid, t):
    k = f'{mid}@{t}'
    if k in cache: return cache[k]
    url = 'https://api.manifold.markets/v0/bets?' + urllib.parse.urlencode({'contractId': mid, 'beforeTime': t, 'limit': 1})
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'errata-crowdcal (errata.page; AI agent research)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                b = json.load(r)
            cache[k] = b[0]['createdTime'] if b else None
            time.sleep(0.25)
            return cache[k]
        except Exception:
            time.sleep(2 + 3 * i)
    return None

rows = []
for x in L:
    for a in ('7d', 'c14', 'c30'):
        p = x.get(a)
        if p is None or p >= 0.10: continue
        t = x['close'] - 7 * D if a == '7d' else x['created'] + (14 if a == 'c14' else 30) * D
        left = (x['close'] - t) / D
        if not (0 <= left < 10): continue
        lb = last_bet(x['id'], int(t))
        if lb is None: continue
        rows.append(((t - lb) / D, p, 1 if x['res'] == 'YES' else 0))
json.dump(cache, open(CACHE, 'w'))

def pb(s, y):
    d = [1.0]
    for _, p, _ in s:
        d = [(d[k] if k < len(d) else 0) * (1 - p) + (d[k - 1] * p if k else 0) for k in range(len(d) + 1)]
    return sum(d[:y + 1])

print('A. sub-10% quotes with 0-10 days left, by age of the last trade before the quote')
print('last trade age | quotes | YES | expected | obs/exp | P(<=obs | calibrated, indep.)')
for lo, hi, lab in ((0, 1, '<1 day'), (1, 7, '1-7 days'), (7, 30, '7-30 days'), (30, 1e9, '30+ days')):
    s = [r for r in rows if lo <= r[0] < hi]
    n, y, e = len(s), sum(r[2] for r in s), sum(r[1] for r in s)
    print(f'{lab:>10} | {n:5d} | {y:3d} | {e:6.1f} | {y/e if e else 0:.2f} | {pb(s, y):.2g}')
print(f'total quotes {len(rows)} (per quote, not per family; dependence ignored)')

print('\nB. carry: markets under 10% at T-30d, price at T-7d, by outcome')
for res in ('NO', 'YES'):
    s = [(x['30d'], x['7d']) for x in L if x.get('30d') is not None and x['30d'] < 0.10 and x.get('7d') is not None and x['res'] == res]
    if not s: print(res, 0); continue
    down = sum(1 for a, b in s if b < a - 0.005); flat = sum(1 for a, b in s if abs(b - a) <= 0.005)
    import statistics as st
    print(f'{res}: n={len(s)} median T-30 {st.median(a for a,_ in s):.3f} -> T-7 {st.median(b for _,b in s):.3f}; fell {down}, flat(+-0.5pt) {flat}, rose {len(s)-down-flat}')
