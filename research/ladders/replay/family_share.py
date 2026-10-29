"""Plan #562: which families carry the robust (warm 7 d, peak >= 0.05, >= 1 day) episodes of replay/episodes.jsonl?
Written 29.10 after the hand check found two criteria regimes inside the RemNi AGI family."""
import json, gzip
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
k = [r for r in rows if r['start'] >= max(start(r['early']) or 0, start(r['late']) or 0) + 7 * D and r['peak'] >= .05 and r['days'] >= 1]
c = Counter(r['family'] for r in k); pairs = Counter(r['family'] for r in {(r['family'], r['early'], r['late']): r for r in k}.values())
print(f"robust >=1 d episodes {len(k)}, families {len(c)}, pairs {sum(pairs.values())}")
for f, n in c.most_common(12): print(f"  {n:4d} ep  {pairs[f]:3d} pairs  {f}")
