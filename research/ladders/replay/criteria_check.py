"""Plan #562: for every robust (warm 7 d, peak >= 0.05, >= 1 day) episode pair, are the two markets' resolution texts the
same apart from the date? Normalise: lowercase, strip years, months, day numbers, ordinals, links/mentions; then difflib
ratio. 'same' >= 0.95, 'near' 0.80-0.95, 'differs' < 0.80. Cached in replay/desc/. Written 29.10 after the AGI hand check."""
import json, gzip, os, re, time, difflib, urllib.request
from collections import Counter
D = 86400000
rows = [json.loads(l) for l in open('replay/episodes.jsonl')]
fam = json.load(open('replay/ladders-2026-10-29.json'))['families']
byurl = {m['url']: m['id'] for ms in fam.values() for m in ms}
first = {}
def start(u):
    i = byurl[u]
    if i not in first:
        b = json.load(gzip.open(f'replay/bets/{i}.json.gz')); first[i] = b[0][0] if b else None
    return first[i]
os.makedirs('replay/desc', exist_ok=True)
def desc(u):
    f = f'replay/desc/{byurl[u]}.json'
    if not os.path.exists(f):
        d = json.load(urllib.request.urlopen(urllib.request.Request('https://api.manifold.markets/v0/slug/' + u.rsplit('/', 1)[1],
            headers={'User-Agent': 'errata-ladders (errata.page; AI agent research)'}), timeout=30))
        json.dump({'q': d['question'], 't': d.get('textDescription') or ''}, open(f, 'w')); time.sleep(0.3)
    return json.load(open(f))
M = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)'
def norm(t):   # v2 (29.10, after reading 3 'differs' pairs: link lists and their headings made 2 of 3 false): drop them
    t = t.lower(); t = re.sub(r'https?://\S+|@/?\S+', '\n', t)
    t = '\n'.join(l for l in t.split('\n') if len(l.split()) >= 3 and not l.strip().endswith(':') and '(this question)' not in l)
    t = re.sub(M, ' ', t)
    t = re.sub(r'\b\d+(st|nd|rd|th)?\b', ' ', t); return re.sub(r'\W+', ' ', t).strip()
k = [r for r in rows if r['start'] >= max(start(r['early']) or 0, start(r['late']) or 0) + 7 * D and r['peak'] >= .05 and r['days'] >= 1]
pairs = {(r['early'], r['late']) for r in k}; cls = {}
for a, b in sorted(pairs):
    x = difflib.SequenceMatcher(None, norm(desc(a)['t']), norm(desc(b)['t'])).ratio()
    cls[(a, b)] = 'same' if x >= .95 else 'near' if x >= .80 else 'differs'
json.dump([[a, b, c] for (a, b), c in cls.items()], open('replay/criteria_pairs.json', 'w'), indent=0)
pc = Counter(cls.values()); ec = Counter(cls[(r['early'], r['late'])] for r in k)
print('pairs', dict(pc), '| episodes', dict(ec))
for c in ('same', 'near', 'differs'):
    d = sorted(r['days'] for r in k if cls[(r['early'], r['late'])] == c and r['end'])
    if d: print(f"  {c}: closed {len(d)}, median heal {d[len(d)//2]:.1f} d, same creator {sum(r['same_creator'] for r in k if cls[(r['early'], r['late'])] == c)}")
