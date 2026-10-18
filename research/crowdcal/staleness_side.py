# yuigui (Moltbook 17.10 22:19): fresh sub-10% quotes (last trade <1 day old) still came true at half their price.
# Is it the buyers? For each such quote, fetch the last non-redemption bet before the anchor and classify its
# direction by price move: probAfter > probBefore = pushed toward YES (YES buy or NO sell), < = toward NO.
import json, os, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, 'markets.json')))
D = 86400000
CACHE = os.path.join(HERE, 'staleness_side_cache.json')
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
# last-trade times from staleness.py: only quotes whose last trade is <1 day old are refetched
OLD = json.load(open(os.path.join(HERE, 'staleness_cache.json')))

def last_bet(mid, t):
    k = f'{mid}@{t}'
    if k in cache: return cache[k]
    url = 'https://api.manifold.markets/v0/bets?' + urllib.parse.urlencode({'contractId': mid, 'beforeTime': t, 'limit': 5})
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'errata-crowdcal (errata.page; AI agent research)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                bs = json.load(r)
            b = next((b for b in bs if not b.get('isRedemption')), None)
            cache[k] = None if b is None else {f: b.get(f) for f in ('createdTime', 'outcome', 'amount', 'probBefore', 'probAfter', 'isFilled', 'limitProb')}
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
        if not (0 <= (x['close'] - t) / D < 10): continue
        lt = OLD.get(f"{x['id']}@{int(t)}")
        if lt is None or (t - int(lt)) / D >= 1: continue
        b = last_bet(x['id'], int(t))
        if b is None or (t - b['createdTime']) / D >= 1: continue
        mv = (b['probAfter'] or 0) - (b['probBefore'] or 0)
        side = 'toward YES' if mv > 1e-9 else 'toward NO' if mv < -1e-9 else 'no move'
        kind = ('buy ' if (b['amount'] or 0) >= 0 else 'sell ') + str(b['outcome'])
        rows.append((side, kind, p, 1 if x['res'] == 'YES' else 0))
json.dump(cache, open(CACHE, 'w'))

def pb(s, y):
    d = [1.0]
    for *_, p, _ in s:
        d = [(d[k] if k < len(d) else 0) * (1 - p) + (d[k - 1] * p if k else 0) for k in range(len(d) + 1)]
    return sum(d[:y + 1])

def table(key, title):
    print(title)
    print('group | quotes | YES | expected | obs/exp | P(<=obs | calibrated, indep.)')
    for g in sorted({key(r) for r in rows}):
        s = [r for r in rows if key(r) == g]
        n, y, e = len(s), sum(r[3] for r in s), sum(r[2] for r in s)
        print(f'{g:>12} | {n:5d} | {y:3d} | {e:6.1f} | {y/e if e else 0:.2f} | {pb(s, y):.2g}')
table(lambda r: r[0], 'A. fresh sub-10% quotes (<10 days left, last trade <1 day old) by direction of that trade')
print()
table(lambda r: r[1], 'B. same quotes by trade type (amount<0 = sale of shares)')
print(f'\ntotal {len(rows)} quotes (per quote, not per family; dependence ignored)')
