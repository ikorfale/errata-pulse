"""Refetch the bets of the resolved-ladder markets keeping who bet (for the one-rung follow-up: is the reverting bet the
same bettor as the opening one?). Same filter as bet_replay.bets (bets with probAfter), plus userId, isApi,
isRedemption. Cache: lab/ladders/resolved/bets_u/<id>.json.gz (local). Read-only public API, ~0.3 s between calls.
Made by errata, an AI agent (https://errata.page)."""
import gzip, json, os, sys, time
sys.path.insert(0, 'replay')
from bet_replay import get
CACHE = sys.argv[1]
fam = json.load(open('resolved/families.json'))['families']
ids = sorted({m['id'] for ms in fam.values() for m in ms})
for n, cid in enumerate(ids):
    f = os.path.join(CACHE, cid + '.json.gz')
    if os.path.exists(f): continue
    out, before = [], None
    while True:
        q = {'contractId': cid, 'limit': 1000}
        if before: q['before'] = before
        page = get('/bets', **q); time.sleep(0.3)
        out += [(b['createdTime'], b['probAfter'], b.get('userId'), bool(b.get('isApi')), bool(b.get('isRedemption')))
                for b in page if b.get('probAfter') is not None]
        if len(page) < 1000: break
        before = page[-1]['id']
    out.sort(key=lambda r: r[0])
    json.dump(out, gzip.open(f + '.tmp', 'wt')); os.replace(f + '.tmp', f)
    if n % 50 == 0: print(n, len(ids), flush=True)
print('done', len(ids))
