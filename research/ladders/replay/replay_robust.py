"""Robust cuts of replay/episodes.jsonl (written after seeing the raw summary, 29.10): drop episodes that start within
7 days of the younger market's first bet (opening prices), then require peak >= 0.05 and >= 1 hour."""
import json, gzip, os
from statistics import median
H = 3600000; D = 24 * H
first = {}
def f0(url, fam):
    return None
rows = [json.loads(l) for l in open('replay/episodes.jsonl')]
fam = json.load(open('replay/ladders-2026-10-29.json'))['families']
byurl = {m['url']: m['id'] for ms in fam.values() for m in ms}
def start(u):
    i = byurl[u]
    if i not in first:
        b = json.load(gzip.open(f'replay/bets/{i}.json.gz')); first[i] = b[0][0] if b else None
    return first[i]
def cut(r, warm, peak, dur):
    s = max(start(r['early']) or 0, start(r['late']) or 0)
    return r['start'] >= s + warm and r['peak'] >= peak and r['days'] * D >= dur
for warm, peak, dur in ((0, .03, 0), (7 * D, .03, 0), (7 * D, .05, H), (7 * D, .05, D), (7 * D, .10, D)):
    k = [r for r in rows if cut(r, warm, peak, dur)]
    pairs = {(r['early'], r['late']) for r in k}; c = [r for r in k if r['end']]
    d = sorted(r['days'] for r in c)
    print(f"warm {warm//D}d peak>={peak} dur>={dur/H:.0f}h: episodes {len(k)} in {len(pairs)} pairs, open {len(k)-len(c)}, "
          f"closed median {median(d) if d else 0:.2f} d, <1 d {sum(x < 1 for x in d)}, same creator {sum(r['same_creator'] for r in k)}")
