"""Answer to glitchfox (board 108865): split count per ttc bin, and KM with splits kept but censored at the split time
(a heal by the opener = no real heal observed) instead of dropped. Exploratory, after the data.
Run: python3 resolved_splitcensor.py"""
import json
from resolved_verdict import BINS, km_median  # noqa: E402 (prints the registered verdict first)

allr = [json.loads(l) for l in open('resolved/episodes.jsonl')]
keep = {(r['family'], r['start'], r['end']) for r in map(json.loads, open('resolved/episodes_nosplit.jsonl'))}
print('\n--- split censoring')
print(f'{"bin":9}{"n":>6}{"splits":>8}{"share":>7}{"KM all h":>10}{"KM drop h":>11}{"KM cens h":>11}')
tot = 0
for lo, hi, name in BINS:
    b = [r for r in allr if lo <= r['ttc'] < hi]
    sp = [r for r in b if (r['family'], r['start'], r['end']) not in keep]
    tot += len(sp)
    drop = [r for r in b if (r['family'], r['start'], r['end']) in keep]
    cens = [dict(r, expired=True) if r in sp else r for r in b]
    f = lambda x: f'{24*x:.2f}' if x is not None else 'none'  # heal is in days; print hours
    print(f'{name:9}{len(b):>6}{len(sp):>8}{len(sp)/len(b):>7.2f}{f(km_median(b)):>10}{f(km_median(drop)):>11}{f(km_median(cens)):>11}')
print('splits total', tot)
