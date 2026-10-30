"""Verdict for PREDICT-resolved-1030.md from resolved/episodes.jsonl (written after the prediction, before reading data).
KM median heal per ttc bin (expired = censored), heal/ttc among healed, expiry share; plus a per-family view so one big
family cannot carry a bin. Run: python3 resolved_verdict.py"""
import json
from collections import defaultdict
from statistics import median

rows = [json.loads(l) for l in open('resolved/episodes.jsonl')]
BINS = [(0, 7, '<7'), (7, 30, '7-30'), (30, 180, '30-180'), (180, 365, '180-365'), (365, 1e9, '>365')]


def km_median(eps):
    """Kaplan-Meier median of heal time; expired episodes censored at their heal (= ttc). None if survival stays > 0.5."""
    s, n = 1.0, len(eps)
    for t, ev in sorted((e['heal'], not e['expired']) for e in eps):
        if ev:
            s *= (n - 1) / n
            if s <= 0.5:
                return t
        n -= 1
    return None


fams = {r['family'] for r in rows}
print(f'episodes {len(rows)}, families with an episode {len(fams)}, expired {sum(r["expired"] for r in rows)}')
out = {}
for lo, hi, name in BINS:
    b = [r for r in rows if lo <= r['ttc'] < hi]
    healed = [r for r in b if not r['expired']]
    fb = defaultdict(list)
    for r in b: fb[r['family']].append(r)
    big = max(fb.values(), key=len) if fb else []
    o = {'n': len(b), 'families': len(fb), 'top_family_share': round(len(big) / len(b), 2) if b else None,
         'km_median': km_median(b) if b else None,
         'heal_over_ttc': round(median(r['heal'] / r['ttc'] for r in healed if r['ttc'] > 0), 4) if healed else None,
         'expired_share': round(sum(r['expired'] for r in b) / len(b), 3) if b else None,
         'median_peak': round(median(r['peak'] for r in b), 3) if b else None}
    # leave-biggest-family-out
    rest = [r for r in b if r['family'] != (big[0]['family'] if big else None)]
    o['km_median_wo_top'] = km_median(rest) if rest else None
    out[name] = o
    print(name, o)
ok = [n for _, _, n in BINS if out[n]['n'] >= 20]
meds = [out[n]['km_median'] for n in ok]
print('P1 bins>=20:', ok, 'KM medians', meds,
      'monotone' if all(x is not None and y is not None and x <= y for x, y in zip(meds, meds[1:])) else 'NOT monotone')
print('P2 heal/ttc >365 vs 7-30:', out['>365']['heal_over_ttc'], out['7-30']['heal_over_ttc'])
print('P3 expired share <7:', out['<7']['expired_share'], 'n', out['<7']['n'])
json.dump(out, open('resolved/verdict.json', 'w'), indent=1)
