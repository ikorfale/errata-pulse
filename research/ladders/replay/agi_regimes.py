"""Plan #562: split the AGI family's robust episodes by criteria regime (description has the Nov 2025 MOD EDIT that defers
to 'In what specific year will we hit AGI?' vs not). Cross-regime pairs are not clean ladder violations. 29.10."""
import json, gzip, time, urllib.request
D = 86400000
rows = [json.loads(l) for l in open('replay/episodes.jsonl')]
fam = json.load(open('replay/ladders-2026-10-29.json'))['families']
F = 'will we get agi before'
byurl = {m['url']: m['id'] for ms in fam.values() for m in ms}
first = {}
def start(u):
    i = byurl[u]
    if i not in first:
        b = json.load(gzip.open(f'replay/bets/{i}.json.gz')); first[i] = b[0][0] if b else None
    return first[i]
reg = {}
for m in fam[F]:
    slug = m['url'].rsplit('/', 1)[1]
    d = json.load(urllib.request.urlopen(urllib.request.Request('https://api.manifold.markets/v0/slug/' + slug,
        headers={'User-Agent': 'errata-ladders (errata.page; AI agent research)'}), timeout=30))
    reg[m['url']] = 'mod' if 'MOD EDIT' in (d.get('textDescription') or '') else 'orig'
    time.sleep(0.3)
json.dump(reg, open('replay/agi_regimes.json', 'w'), indent=1)
print('markets', len(reg), {r: list(reg.values()).count(r) for r in set(reg.values())})
k = [r for r in rows if r['family'] == F and r['start'] >= max(start(r['early']) or 0, start(r['late']) or 0) + 7 * D
     and r['peak'] >= .05 and r['days'] >= 1]
for lab in ('mod-mod', 'orig-orig', 'cross'):
    s = [r for r in k if (lab == 'cross') == (reg[r['early']] != reg[r['late']]) and (lab == 'cross' or reg[r['early']] == lab[:lab.find('-')])]
    print(f"{lab}: episodes {len(s)}, pairs {len({(r['early'], r['late']) for r in s})}")
