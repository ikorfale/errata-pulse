"""Calibration of resolved Manifold war/geopolitics markets at T-30d and T-7d (see PREREG.md)."""
import json, time, urllib.request, urllib.parse, sys
API = 'https://api.manifold.markets/v0'
TERMS = ['ukraine', 'russia', 'putin', 'nato', 'war', 'ceasefire', 'invasion', 'missile', 'nuclear', 'iran',
         'israel', 'gaza', 'houthi', 'taiwan', 'china military', 'mobilization', 'coup', 'sanctions']
CUTOFF = 1790812800000  # 2026-10-01T00:00Z
HOR = {'30d': 30 * 86400000, '7d': 7 * 86400000}

def get(path, **q):
    url = API + path + '?' + urllib.parse.urlencode(q)
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'errata-crowdcal (errata.page; AI agent research)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(2 + 3 * i)
    raise SystemExit('failed ' + url)

markets = {}
for t in TERMS:
    for off in range(0, 1000, 100):
        page = get('/search-markets', term=t, filter='resolved', contractType='BINARY', limit=100, offset=off, sort='most-popular')
        time.sleep(0.3)
        for m in page:
            if m.get('resolution') in ('YES', 'NO') and (m.get('uniqueBettorCount') or 0) >= 20 \
                    and (m.get('closeTime') or 0) < CUTOFF and m['id'] not in markets:
                m['_term'] = t
                markets[m['id']] = m
        if len(page) < 100:
            break
print('markets', len(markets), file=sys.stderr)
rows = []
for i, (mid, m) in enumerate(markets.items()):
    close = min(m['closeTime'], m.get('resolutionTime') or m['closeTime'])
    r = {'id': mid, 'q': m['question'], 'term': m['_term'], 'res': m['resolution'], 'close': close,
         'created': m['createdTime'], 'bettors': m['uniqueBettorCount'], 'url': m.get('url')}
    for h, ms in HOR.items():
        t = close - ms
        if t <= m['createdTime']:
            r[h] = None
            continue
        b = get('/bets', contractId=mid, limit=1, beforeTime=t)
        time.sleep(0.25)
        r[h] = b[0]['probAfter'] if b else None
    rows.append(r)
    if i % 50 == 0:
        print(i, file=sys.stderr)
json.dump(rows, open('markets.json', 'w'), indent=0, ensure_ascii=False)
print('done', len(rows))
