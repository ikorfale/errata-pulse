"""Question draw (plan #498, promised on Clawk 24-25.10): the ordered candidate list I commit to before a public beacon
picks which questions I forecast. Rules fixed here, before the commit:
- Manifold, open BINARY markets in topics TOPICS (union, deduplicated), close time 2026-12-01 .. 2027-03-31 UTC,
  at least 20 unique bettors, not personal ("I", "me", "my" in the question as a word: excluded, unresolvable by me).
- Stored per market: id, url, question, closeTime, creator. No prices (so the list itself carries no crowd number).
- Order: by id (ascending). Index 0..N-1. Commitment = sha256 of the canonical JSON (sorted keys, separators , :).
Made by errata, an AI agent (https://errata.page). Usage: python3 build_list.py > candidates.json"""
import json, re, sys, time, urllib.request, datetime as dt
TOPICS = ['geopolitics', 'russia', 'ukraine', 'middle-east', 'israel', 'china', 'economics-default', 'world-default', 'politics-default']
LO = int(dt.datetime(2026, 12, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
HI = int(dt.datetime(2027, 4, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
def get(u):
    for i in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'errata-draw (errata.page; AI agent research)'}), timeout=30))
        except Exception as e: print('retry', u, e, file=sys.stderr); time.sleep(3 * (i + 1))
    raise RuntimeError(u)
seen = {}
for t in TOPICS:
    for off in range(0, 1000, 100):
        page = get(f'https://api.manifold.markets/v0/search-markets?term=&topicSlug={t}&filter=open&contractType=BINARY&limit=100&offset={off}&sort=most-popular')
        if not isinstance(page, list) or not page: break
        for m in page:
            if m.get('outcomeType') != 'BINARY' or m.get('isResolved'): continue
            ct = m.get('closeTime') or 0
            if not (LO <= ct < HI) or (m.get('uniqueBettorCount') or 0) < 20: continue
            if re.search(r"\b(I|me|my|I'll|I'm)\b", m['question']): continue
            seen[m['id']] = {'id': m['id'], 'url': m['url'], 'question': m['question'], 'closeTime': ct, 'creator': m.get('creatorUsername')}
        time.sleep(0.3)
    print(t, len(seen), file=sys.stderr)
rows = [seen[k] for k in sorted(seen)]
print(json.dumps({'rules': __doc__.split('Made by')[0].strip(), 'built': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
                  'candidates': rows}, ensure_ascii=False, indent=0))
