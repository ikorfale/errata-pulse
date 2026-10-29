"""glitchfox 107630: family-weighted KM as a sensitivity row. Each episode gets weight 1/n_f (n_f = episodes of its family
in that arm), so every family counts once; weighted at-risk and event mass. KM medians for clean, mixed and mixed without
AGI, and the family-cluster bootstrap (2000 draws, seed 1029, as family_boot.py) of the weighted difference and the clean
weighted median. Same cut and classes as censor_check.py. Written 29.10 12:55 UTC (date -u)."""
import random, sys
from collections import defaultdict
sys.argv = ['x']; src = open('censor_check.py').read().split("for name, sel in")[0]; exec(src)
def wkm(D):
    t = sorted((r['days'], r['end'] is not None, 1 / len(v)) for v in D.values() for r in v)
    n = sum(w for *_, w in t); s = 1.0; i = 0
    while i < len(t):
        x = t[i][0]; d = c = 0
        while i < len(t) and t[i][0] == x: d += t[i][2] * t[i][1]; c += t[i][2]; i += 1
        if d: s *= 1 - d / n
        n -= c
        if s <= .5: return x
    return None
C = defaultdict(list); M = defaultdict(list)
for r in k: (C if cls[(r['early'], r['late'])] == 'same' else M)[r['family']].append(r)
noagi = {f: v for f, v in M.items() if not f.startswith('will we get agi')}
def rs(D, rng):
    fs = list(D); return {i: D[f] for i, f in enumerate(rng.choice(fs) for _ in fs)}
for lab, Mf in (('all mixed', M), ('mixed without AGI', noagi)):
    rng = random.Random(1029); out = []
    for _ in range(2000):
        a, b = wkm(rs(Mf, rng)), wkm(rs(C, rng))
        if a is not None and b is not None: out.append(a - b)
    out.sort(); lo, hi = out[int(.025 * len(out))], out[int(.975 * len(out))]
    print(f"{lab}: family-weighted KM median mixed {wkm(Mf):.1f} d ({len(Mf)} families) vs clean {wkm(C):.1f} d ({len(C)} families), "
          f"diff {wkm(Mf) - wkm(C):+.1f}; family bootstrap 95% {lo:+.1f} .. {hi:+.1f} ({len(out)} draws)")
rng = random.Random(7); bm = sorted(x for x in (wkm(rs(C, rng)) for _ in range(2000)) if x is not None)
print(f"clean family-weighted KM median, family bootstrap 95%: {bm[int(.025 * len(bm))]:.1f} .. {bm[int(.975 * len(bm))]:.1f} d ({len(bm)} draws)")
