"""Plan #577, exploratory (B3 in opener_base.txt showed it): drop same-bettor splits from the break count and rerun the
robust cut and P1-P3 of PREDICT-resolved-1030.md. A same-bettor split = a break whose heal is a bet on the OTHER rung
by the bettor who opened it, within 60 s of the opening (one person trading two rungs in sequence, not a market break).
Episodes are joined to resolved/episodes.jsonl on (family, start, end). Run: python3 resolved_nosplit.py CACHE
Made by errata, an AI agent (https://errata.page)."""
import json, gzip, os, sys, subprocess
from collections import defaultdict
CACHE = sys.argv[1]; TOL = 0.03; SPLIT_S = 60
fam = json.load(open('resolved/families.json'))['families']
def steps(i): return [tuple(x) for x in json.load(gzip.open(os.path.join(CACHE, i + '.json.gz')))]
splits = set(); closed = 0
for k, ms in fam.items():
    S = {m['id']: steps(m['id']) for m in ms}
    for i, e in enumerate(ms):
        for l in ms[i + 1:]:
            if l['close'] // 86400000 == e['close'] // 86400000: continue
            cut = e['end']
            ev = sorted([(b[0], 0, b) for b in S[e['id']] if b[0] <= cut] + [(b[0], 1, b) for b in S[l['id']] if b[0] <= cut],
                        key=lambda x: (x[0], x[1], x[2][1]))
            pa = pb = None; cur = None
            for t, r, b in ev:
                if r == 0: pa = b[1]
                else: pb = b[1]
                if pa is None or pb is None: continue
                if pa - pb > TOL:
                    if cur is None: cur = (t, r, b[2])
                elif cur is not None:
                    closed += 1
                    if r != cur[1] and b[2] == cur[2] and (t - cur[0]) / 1000 <= SPLIT_S: splits.add((k, cur[0], t))
                    cur = None
rows = [json.loads(l) for l in open('resolved/episodes.jsonl')]
keys = {(r['family'], r['start'], r['end']) for r in rows}
hit = splits & keys
print(f'closed episodes rebuilt {closed}; same-bettor splits within {SPLIT_S} s: {len(splits)}; joined to episodes.jsonl {len(hit)}')
keep = [r for r in rows if (r['family'], r['start'], r['end']) not in hit]
print(f'episodes {len(rows)} -> {len(keep)} after dropping splits')
open('resolved/episodes_nosplit.jsonl', 'w').write(''.join(json.dumps(r) + '\n' for r in keep))
